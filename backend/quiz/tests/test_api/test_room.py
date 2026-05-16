from django.test import TestCase
from quiz.models import Quiz
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock


class RoomApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test", password="pass")
        self.client.force_authenticate(user=self.user)

        Quiz.objects.create(name="sample_quiz")

    @patch("quiz.views.room_views.redis_client")
    @patch("quiz.views.room_views.random.choices")
    def test_cr_room(self, mock_random, mock_redis):

        mock_redis.exists = MagicMock(return_value=False)
        mock_random.return_value = "ABC"

        response = self.client.post(
            "/api/create_room/",
            {"quiz_name": "sample_quiz"},
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        mock_redis.hset.assert_called_once_with(
            "room:ABC",
            mapping={
                "owner": "test",
                "status": "waiting",
                "quiz_name": "sample_quiz"
            }
        )