import uuid

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from histories.models import QuizHistory
from quizzes.models import Quiz


class StatsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test", password="pass")
        self.client.force_authenticate(user=self.user)
        self.quiz = Quiz.objects.create(name="sample_quiz")

    def test_user_stats(self):
        QuizHistory.objects.create(user=self.user, quiz=self.quiz, score=10)

        response = self.client.get("/api/user_stats/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_user_stats_per_day(self):
        for score in (5, 7):
            QuizHistory.objects.create(
                user=self.user,
                quiz=self.quiz,
                score=score,
                quiz_time=timezone.now().date(),
            )

        response = self.client.get("/api/user_stats_per_day/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data[0],
            {
                "date": str(timezone.now().date()),
                "quizzes_played": 2,
            },
        )

    def test_ranking(self):
        game_id = uuid.uuid4()
        QuizHistory.objects.create(
            user=self.user,
            quiz=self.quiz,
            game_id=game_id,
            score=10,
        )

        response = self.client.get(f"/api/quiz_history/{game_id}/ranking/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["game_id"], str(game_id))
        self.assertEqual(response.data["quiz_name"], "sample_quiz")
        self.assertEqual(response.data["own_score"], 10)
        self.assertEqual(
            response.data["ranking"],
            [{"username": "test", "score": 10}],
        )
