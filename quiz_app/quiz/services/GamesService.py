import time
import json
import redis.asyncio as redis
from django.conf import settings
from quiz.models import Quiz, Question
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


class GameService:
    """
    Service class for handling real-time quiz game logic using Redis for state 
    management and PostgreSQL for persistent data.

    """

    QUESTION_TIME = 3  
    ROOM_TTL = 3600    # max czas zycia wpisu w redis

    @staticmethod
    def get_keys(room_code, username=None):
        """
        Generate standardized Redis keys for various game state components.

        Args:
            room_code (str): The unique identifier for the game room.
            username (str, optional): The player's username for user-specific keys.

        Returns:
            tuple: A triple containing (room_key, users_key, ans_key).
                   ans_key is None if no username is provided.
        """
        room_key = f"room:{room_code}"
        users_key = f"{room_key}:users"
        ans_key = f"game:{room_code}:{username}" if username else None
        return room_key, users_key, ans_key

    @classmethod
    async def get_initial_state(cls, room_code, username):
        """
        Validate if a user can join the room and retrieve the current room data.

        Checks for room existence, user membership in the room's set, 
        and if the game status is currently set to 'playing'.

        Args:
            room_code (str): The unique identifier for the room.
            username (str): The username of the player attempting to connect.

        Returns:
            tuple: (room_data, error_code)
                - room_data (dict|None): Hash map of room state from Redis.
                - error_code (str|None): Error identifier if validation fails.
        """
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
        """
        Persist a player's answer for the current question in Redis.

        Args:
            room_code (str): The unique identifier for the room.
            username (str): The player's username.
            answer (int|str): The index or value of the chosen answer.

        Returns:
            bool: True if the answer was saved, False if no active question was found.
        """
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
        """
        Update the room state with the metadata of the currently active question.

        Stores the question text and answers (JSON encoded) along with the 
        start timestamp to allow reconnecting users to synchronize.

        Args:
            room_code (str): The unique identifier for the room.
            index (int): The sequence index of the question in the quiz.
            question_data (dict): Dictionary containing 'text' and 'answers' list.
        """
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
        """
        Retrieve the active question data for synchronization/reconnection.

        Args:
            room_code (str): The unique identifier for the room.

        Returns:
            dict|None: Reconstructed question data including start_time, 
                       or None if no active question is found.
        """
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
        """
        Flag the game session as completed in Redis.

        Args:
            room_code (str): The unique identifier for the room.
        """
        room_key, _, _ = cls.get_keys(room_code)
        await redis_client.hset(room_key, "is_run", "end")

    @classmethod
    async def get_questions_by_quiz_name(cls, quiz_name="sample"):
        """
        Fetch all questions associated with a specific quiz from the database.

        Uses sync_to_async to perform safe database operations within 
        an asynchronous context.

        Args:
            quiz_name (str): The name of the quiz to retrieve.

        Returns:
            list: A list of dictionaries, each representing a question with its
                  text, possible answers, and correct answer index.
        """
        @sync_to_async
        def fetch_questions():
            try:
                quiz = Quiz.objects.get(name=quiz_name)
            except ObjectDoesNotExist:
                return []

            qs = Question.objects.filter(quiz=quiz).order_by("id")
            return [
                {
                    "id": q.id,
                    "text": q.text,
                    "answers": [q.ans1, q.ans2],
                    "correct_ans": q.correct_ans
                }
                for q in qs
            ]

        return await fetch_questions()

    @classmethod
    async def get_score(cls, room_code, username, quiz_name):
        """
        Calculate the total score for a player based on their answers in Redis.

        Compares user answers stored in Redis against the 'correct_ans' 
        field in the PostgreSQL database.

        Args:
            room_code (str): The unique identifier for the room.
            username (str): The username of the player.
            quiz_name (str): The name of the quiz for correct answer validation.

        Returns:
            int: The count of correct answers provided by the player.
        """
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
                except (ValueError, TypeError):
                    continue
                if user_ans == q["correct_ans"]:
                    score += 1
        return score

    @classmethod
    async def get_users_in_room(cls, room_code):
        """
        Retrieve the list of all unique usernames currently registered in the room.

        Args:
            room_code (str): The unique identifier for the room.

        Returns:
            set: A set of usernames (strings) retrieved from the Redis room set.
        """
        _, users_key, _ = cls.get_keys(room_code)
        return await redis_client.smembers(users_key)