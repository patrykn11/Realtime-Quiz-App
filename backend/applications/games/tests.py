from unittest.mock import AsyncMock, MagicMock, patch

from asgiref.sync import async_to_sync
from django.test import TestCase

from applications.choices.models import Choice
from applications.games.services import GameService
from applications.questions.models import Question
from applications.quizzes.models import Quiz


class GameServiceTest(TestCase):
    def setUp(self):
        quiz = Quiz.objects.create(name="sample")
        question = Question.objects.create(quiz=quiz, text="2+2")
        Choice.objects.create(question=question, text="3", is_correct=False)
        Choice.objects.create(question=question, text="4", is_correct=True)

    def test_get_keys(self):
        room_key, users_key, answers_key = GameService.get_keys("room1", "john")

        self.assertEqual(room_key, "room:room1")
        self.assertEqual(users_key, "room:room1:users")
        self.assertEqual(answers_key, "game:room1:john")

    def test_get_questions_by_quiz(self):
        result = async_to_sync(GameService.get_questions_by_quiz_name)("sample")

        self.assertEqual(result[0]["answers"], ["3", "4"])
        self.assertEqual(result[0]["correct_ans"], 1)

    @patch("applications.games.services.redis_client")
    def test_get_score(self, mock_redis):
        mock_redis.hgetall = AsyncMock(side_effect=[{"0": "1"}, {"0": "1"}])

        score = async_to_sync(GameService.get_score)("room1", "john", "sample")

        self.assertEqual(score, 1)

    @patch("applications.games.services.redis_client")
    def test_get_current_question(self, mock_redis):
        mock_redis.hgetall = AsyncMock(
            return_value={
                "current_question_text": "2+2",
                "current_question_answers": '["3", "4"]',
                "start_time": "123",
            }
        )

        result = async_to_sync(GameService.get_current_question)("room1")

        self.assertEqual(result["text"], "2+2")
        self.assertEqual(result["answers"], ["3", "4"])

    @patch("applications.games.services.redis_client")
    def test_save_answer(self, mock_redis):
        mock_redis.hget = AsyncMock(return_value="0")
        mock_pipe = AsyncMock()
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = mock_pipe
        mock_context.__aexit__.return_value = None
        mock_redis.pipeline = MagicMock(return_value=mock_context)

        result = async_to_sync(GameService.save_answer)("room1", "john", 1)

        self.assertTrue(result)
        mock_pipe.execute.assert_awaited_once()

    @patch("applications.games.services.redis_client")
    def test_get_users_in_room(self, mock_redis):
        mock_redis.smembers = AsyncMock(return_value={"john", "anna"})

        result = async_to_sync(GameService.get_users_in_room)("room1")

        self.assertIn("john", result)
        self.assertIn("anna", result)
