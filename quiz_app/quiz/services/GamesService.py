import time
import json
import redis.asyncio as redis
from django.conf import settings
from quiz.models import Quiz, Question, Choice, QuizHistory 
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

class GameService:
    QUESTION_TIME = 10  
    ROOM_TTL = 3600    

    @staticmethod
    def get_keys(room_code, username=None):
        room_key = f"room:{room_code}"
        users_key = f"{room_key}:users"
        ans_key = f"game:{room_code}:{username}" if username else None
        return room_key, users_key, ans_key

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

        questions = await cls.get_questions_by_quiz_name(quiz_name)
        score = 0
        for idx, q in enumerate(questions):
            q_id_str = str(idx)
            if q_id_str in user_answers:
                try:
                    user_ans = int(user_answers[q_id_str])
                    if user_ans == q["correct_ans"]:
                        score += 1
                except (ValueError, TypeError):
                    continue
        return score
    
    @classmethod
    async def save_quiz(cls, room_code, quiz_name):
        usernames = await cls.get_users_in_room(room_code)
        quiz = await sync_to_async(Quiz.objects.get)(name=quiz_name)

        for username in usernames:
            score = await cls.get_score(room_code, username, quiz_name)
            user = await sync_to_async(User.objects.get)(username=username)
            await sync_to_async(QuizHistory.objects.create)(user=user, quiz=quiz, score=score)

    @classmethod
    async def get_quiz_name(cls, room_code):
        room_key, _, _ = cls.get_keys(room_code)
        return await redis_client.hget(room_key, "quiz_name")

    @classmethod
    async def get_users_in_room(cls, room_code):
        _, users_key, _ = cls.get_keys(room_code)
        return await redis_client.smembers(users_key)