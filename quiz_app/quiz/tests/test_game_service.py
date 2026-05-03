from django.test import TestCase
from unittest.mock import AsyncMock, patch, MagicMock
from asgiref.sync import async_to_sync

from quiz.models import Quiz, Question, Choice
from quiz.services.GamesService import GameService

class GameServiceTest(TestCase):

    def setUp(self):
        self.quiz = Quiz.objects.create(name="sample")
        self.question = Question.objects.create(
            quiz=self.quiz,
            text="2+2"
        )
        Choice.objects.create(question=self.question, text="3", is_correct=False)
        Choice.objects.create(question=self.question, text="4", is_correct=True)

    def test_get_keys(self):
        room_key, users_key, ans_key = GameService.get_keys("room1", "john")

        self.assertEqual(room_key, "room:room1")
        self.assertEqual(users_key, "room:room1:users")
        self.assertEqual(ans_key, "game:room1:john")

    def test_get_questions_by_quiz(self):
        result = async_to_sync(GameService.get_questions_by_quiz_name)("sample")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["text"], "2+2")
        self.assertEqual(result[0]["answers"], ["3", "4"])
        self.assertEqual(result[0]["correct_ans"], 1)

    @patch("quiz.services.GamesService.redis_client")
    def test_get_score(self, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={
            "0": "1"
        })

        score = async_to_sync(GameService.get_score)(
            "room1", "john", "sample"
        )

        self.assertEqual(score, 1)

    @patch("quiz.services.GamesService.redis_client")
    def test_get_current_question(self, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={
            "current_question_text": "2+2",
            "current_question_answers": '["3","4"]',
            "start_time": "123"
        })

        result = async_to_sync(GameService.get_current_question)("room1")

        self.assertEqual(result["text"], "2+2")
        self.assertEqual(result["answers"], ["3", "4"])

    @patch("quiz.services.GamesService.redis_client")
    def test_save_answer(self, mock_redis):
        mock_redis.hget = AsyncMock(return_value="0")
        mock_pipe = AsyncMock()
        mock_pipe.hset = AsyncMock()
        mock_pipe.expire = AsyncMock()
        mock_pipe.execute = AsyncMock()
        mock_cm = MagicMock()
        mock_cm.__aenter__.return_value = mock_pipe
        mock_cm.__aexit__.return_value = None
        mock_redis.pipeline = MagicMock(return_value=mock_cm)

        result = async_to_sync(GameService.save_answer)(
            "room1", "john", 1
        )

        self.assertTrue(result)
        mock_pipe.hset.assert_called_once()
        mock_pipe.expire.assert_called_once()
        mock_pipe.execute.assert_called_once()

    @patch("quiz.services.GamesService.redis_client")
    def test_get_users_in_room(self, mock_redis):
        mock_redis.smembers = AsyncMock(return_value={"john", "anna"})

        result = async_to_sync(GameService.get_users_in_room)("room1")

        self.assertIn("john", result)
        self.assertIn("anna", result)