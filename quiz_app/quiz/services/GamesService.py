import time
import json
import uuid
from quiz.models import Quiz, Question, Choice, QuizHistory 
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from quiz.redis_client import async_redis_client as redis_client

class GameService:
    QUESTION_TIME = 3  
    ROOM_TTL = 3600    

    @staticmethod
    def get_keys(room_code, username=None):
        room_key = f"room:{room_code}"
        users_key = f"{room_key}:users"
        ans_key = f"game:{room_code}:{username}" if username else None
        return room_key, users_key, ans_key

    @staticmethod
    def get_correct_answers_key(room_code):
        return f"game:{room_code}:correct_answers"

    @classmethod
    async def get_initial_state(cls, room_code, username):
        room_key, users_key, _ = cls.get_keys(room_code)
        room_data = await redis_client.hgetall(room_key)
        
        if not room_data:
            return None, "room_not_found"

        is_member = await redis_client.sismember(users_key, username)
        if not is_member:
            return None, "not_a_member"

        if room_data.get("status") != "playing":
            return None, "game_not_playing"

        return room_data, None

    @classmethod
    async def save_answer(cls, room_code, username, answer):
        room_key, _, ans_key = cls.get_keys(room_code, username)
        current_q = await redis_client.hget(room_key, "current_question")

        if current_q is not None:
            async with redis_client.pipeline(transaction=True) as pipe:
                await pipe.hset(ans_key, current_q, str(answer))
                await pipe.expire(ans_key, cls.ROOM_TTL)
                await pipe.execute()
            return True
        return False

    @classmethod
    async def set_correct_answers(cls, room_code, questions):
        correct_answers_key = cls.get_correct_answers_key(room_code)
        mapping = {
            str(index): str(question["correct_ans"])
            for index, question in enumerate(questions)
        }

        if not mapping:
            return

        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.delete(correct_answers_key)
            await pipe.hset(correct_answers_key, mapping=mapping)
            await pipe.expire(correct_answers_key, cls.ROOM_TTL)
            await pipe.execute()

    @classmethod
    async def set_current_question(cls, room_code, index, question_data):
        room_key, _, _ = cls.get_keys(room_code)
        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.hset(room_key, mapping={
                "current_question": index,
                "current_question_text": question_data["text"],
                "current_question_answers": json.dumps(question_data["answers"]),
                "start_time": str(time.time()),
                "is_run": "true"
            })
            await pipe.expire(room_key, cls.ROOM_TTL)
            await pipe.execute()

    @classmethod
    async def get_current_question(cls, room_code):
        room_key, _, _ = cls.get_keys(room_code)
        data = await redis_client.hgetall(room_key)
        
        if not data or "current_question_text" not in data:
            return None

        return {
            "text": data["current_question_text"],
            "answers": json.loads(data["current_question_answers"]),
            "start_time": data["start_time"]
        }

    @classmethod
    async def set_game_finished(cls, room_code):
        room_key, _, _ = cls.get_keys(room_code)
        await redis_client.hset(room_key, "is_run", "end")

    @classmethod
    async def get_questions_by_quiz_name(cls, quiz_name):
        @sync_to_async
        def fetch_questions():
            try:
                quiz = Quiz.objects.get(name=quiz_name)
            except ObjectDoesNotExist:
                return []

            qs = Question.objects.filter(quiz=quiz).order_by("id")
            result = []
            for q in qs:
                choices = list(q.choices.all())
                choice_texts = [c.text for c in choices]
                correct_idx = 0
                for i, c in enumerate(choices):
                    if c.is_correct:
                        correct_idx = i
                        break
                
                result.append({
                    "id": q.id,
                    "text": q.text,
                    "answers": choice_texts,
                    "correct_ans": correct_idx
                })
            return result

        return await fetch_questions()

    @classmethod
    async def get_score(cls, room_code, username, quiz_name):
        _, _, ans_key = cls.get_keys(room_code, username)
        user_answers = await redis_client.hgetall(ans_key)
        if not user_answers:
            return 0

        correct_answers = await redis_client.hgetall(cls.get_correct_answers_key(room_code))
        if not correct_answers:
            questions = await cls.get_questions_by_quiz_name(quiz_name)
            correct_answers = {
                str(index): str(question["correct_ans"])
                for index, question in enumerate(questions)
            }

        score = 0
        for question_index, correct_answer in correct_answers.items():
            if question_index not in user_answers:
                continue

            try:
                user_ans = int(user_answers[question_index])
                if user_ans == int(correct_answer):
                    score += 1
            except (ValueError, TypeError):
                continue
        return score

    @classmethod
    async def get_question_results(cls, room_code, question_index):
        _, users_key, _ = cls.get_keys(room_code)
        correct_answers_key = cls.get_correct_answers_key(room_code)
        correct_answer = await redis_client.hget(correct_answers_key, str(question_index))
        users = await redis_client.smembers(users_key)

        results = []
        for username in users:
            _, _, ans_key = cls.get_keys(room_code, username)
            answer = await redis_client.hget(ans_key, str(question_index))

            try:
                answer_index = int(answer) if answer is not None else None
                is_correct = answer_index == int(correct_answer)
            except (ValueError, TypeError):
                answer_index = None
                is_correct = False

            results.append({
                "username": username,
                "answer": answer_index,
                "is_correct": is_correct
            })

        return {
            "correct_answer": int(correct_answer) if correct_answer is not None else None,
            "results": sorted(results, key=lambda item: item["username"])
        }
    
    @classmethod
    async def save_quiz(cls, room_code, quiz_name):
        usernames = await cls.get_users_in_room(room_code)
        quiz = await sync_to_async(Quiz.objects.get)(name=quiz_name)
        game_id = uuid.uuid4()

        for username in usernames:
            score = await cls.get_score(room_code, username, quiz_name)
            user = await sync_to_async(User.objects.get)(username=username)
            await sync_to_async(QuizHistory.objects.create)(
                game_id=game_id,
                user=user,
                quiz=quiz,
                score=score
            )

    @classmethod
    async def get_quiz_name(cls, room_code):
        room_key, _, _ = cls.get_keys(room_code)
        return await redis_client.hget(room_key, "quiz_name")

    @classmethod
    async def get_users_in_room(cls, room_code):
        _, users_key, _ = cls.get_keys(room_code)
        return await redis_client.smembers(users_key)
