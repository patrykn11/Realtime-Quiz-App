import json
import time
import uuid

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from common.redis import async_redis_client as redis_client
from histories.models import QuizHistory
from questions.models import Question
from quizzes.models import Quiz


class GameService:
    QUESTION_TIME = 3
    ROOM_TTL = 3600

    @staticmethod
    def get_keys(room_code, username=None):
        room_key = f"room:{room_code}"
        users_key = f"{room_key}:users"
        answers_key = f"game:{room_code}:{username}" if username else None
        return room_key, users_key, answers_key

    @staticmethod
    def get_correct_answers_key(room_code):
        return f"game:{room_code}:correct_answers"

    @classmethod
    async def get_initial_state(cls, room_code, username):
        room_key, users_key, _ = cls.get_keys(room_code)
        room_data = await redis_client.hgetall(room_key)
        if not room_data:
            return None, "room_not_found"
        if not await redis_client.sismember(users_key, username):
            return None, "not_a_member"
        if room_data.get("status") != "playing":
            return None, "game_not_playing"
        return room_data, None

    @classmethod
    async def save_answer(cls, room_code, username, answer):
        room_key, _, answers_key = cls.get_keys(room_code, username)
        current_question = await redis_client.hget(room_key, "current_question")
        if current_question is None:
            return False

        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.hset(answers_key, current_question, str(answer))
            await pipe.expire(answers_key, cls.ROOM_TTL)
            await pipe.execute()
        return True

    @classmethod
    async def set_correct_answers(cls, room_code, questions):
        mapping = {
            str(index): str(question["correct_ans"])
            for index, question in enumerate(questions)
        }
        if not mapping:
            return

        key = cls.get_correct_answers_key(room_code)
        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.delete(key)
            await pipe.hset(key, mapping=mapping)
            await pipe.expire(key, cls.ROOM_TTL)
            await pipe.execute()

    @classmethod
    async def set_current_question(cls, room_code, index, question_data):
        room_key, _, _ = cls.get_keys(room_code)
        async with redis_client.pipeline(transaction=True) as pipe:
            await pipe.hset(
                room_key,
                mapping={
                    "current_question": index,
                    "current_question_text": question_data["text"],
                    "current_question_answers": json.dumps(question_data["answers"]),
                    "start_time": str(time.time()),
                    "is_run": "true",
                },
            )
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
            "start_time": data["start_time"],
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

            questions = Question.objects.filter(quiz=quiz).prefetch_related(
                "choices"
            ).order_by("id")
            result = []
            for question in questions:
                choices = list(question.choices.all())
                result.append(
                    {
                        "id": question.id,
                        "text": question.text,
                        "answers": [choice.text for choice in choices],
                        "correct_ans": next(
                            (
                                index
                                for index, choice in enumerate(choices)
                                if choice.is_correct
                            ),
                            0,
                        ),
                    }
                )
            return result

        return await fetch_questions()

    @classmethod
    async def get_score(cls, room_code, username, quiz_name):
        _, _, answers_key = cls.get_keys(room_code, username)
        user_answers = await redis_client.hgetall(answers_key)
        if not user_answers:
            return 0

        correct_answers = await redis_client.hgetall(
            cls.get_correct_answers_key(room_code)
        )
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
                if int(user_answers[question_index]) == int(correct_answer):
                    score += 1
            except (TypeError, ValueError):
                continue
        return score

    @classmethod
    async def get_question_results(cls, room_code, question_index):
        _, users_key, _ = cls.get_keys(room_code)
        correct_answer = await redis_client.hget(
            cls.get_correct_answers_key(room_code), str(question_index)
        )
        users = await redis_client.smembers(users_key)

        results = []
        for username in users:
            _, _, answers_key = cls.get_keys(room_code, username)
            answer = await redis_client.hget(answers_key, str(question_index))
            try:
                answer_index = int(answer) if answer is not None else None
                is_correct = answer_index == int(correct_answer)
            except (TypeError, ValueError):
                answer_index = None
                is_correct = False
            results.append(
                {
                    "username": username,
                    "answer": answer_index,
                    "is_correct": is_correct,
                }
            )

        return {
            "correct_answer": int(correct_answer) if correct_answer is not None else None,
            "results": sorted(results, key=lambda item: item["username"]),
        }

    @classmethod
    async def save_quiz(cls, room_code, quiz_name):
        usernames = await cls.get_users_in_room(room_code)
        quiz = await Quiz.objects.aget(name=quiz_name)
        user_model = get_user_model()
        game_id = uuid.uuid4()

        for username in usernames:
            score = await cls.get_score(room_code, username, quiz_name)
            user = await user_model.objects.aget(username=username)
            await QuizHistory.objects.acreate(
                game_id=game_id,
                user=user,
                quiz=quiz,
                score=score,
            )

    @classmethod
    async def get_quiz_name(cls, room_code):
        room_key, _, _ = cls.get_keys(room_code)
        return await redis_client.hget(room_key, "quiz_name")

    @classmethod
    async def get_users_in_room(cls, room_code):
        _, users_key, _ = cls.get_keys(room_code)
        return await redis_client.smembers(users_key)
