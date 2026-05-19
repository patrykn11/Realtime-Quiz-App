from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from quizzes.models import Quiz


class RoomApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test", password="pass")
        self.client.force_authenticate(user=self.user)
        Quiz.objects.create(name="sample_quiz")

    @patch("rooms.views.redis_client")
    @patch("rooms.views.random.choices")
    def test_create_room(self, mock_random, mock_redis):
        mock_redis.exists = MagicMock(return_value=False)
        mock_random.return_value = "ABC"

        response = self.client.post(
            "/api/create_room/",
            {"quiz_name": "sample_quiz"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        mock_redis.hset.assert_called_once_with(
            "room:ABC",
            mapping={
                "owner": "test",
                "status": "waiting",
                "quiz_name": "sample_quiz",
            },
        )
