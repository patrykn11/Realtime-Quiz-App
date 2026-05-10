from django.test import TestCase
from quiz.models import Quiz, QuizHistory
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.utils import timezone
import uuid

class StatsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test", password="pass")
        self.client.force_authenticate(user=self.user)

        self.quiz = Quiz.objects.create(name="sample_quiz")

    def test_user_stats(self):
        QuizHistory.objects.create(
            user=self.user,
            quiz=self.quiz,
            score=10,
            quiz_time=timezone.now().date()
        )

        response = self.client.get("/api/user_stats/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_user_stats_per_day(self):
        QuizHistory.objects.create(
            user=self.user,
            quiz=self.quiz,
            score=5,
            quiz_time=timezone.now().date()
        )

        QuizHistory.objects.create(
            user=self.user,
            quiz=self.quiz,
            score=7,
            quiz_time=timezone.now().date()
        )

        response = self.client.get("/api/user_stats_per_day/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["quizzes_played"], 2)

    def test_quiz_history_ranking(self):
        user2 = User.objects.create_user(username="user2", password="pass")

        game1 = uuid.uuid4()

        QuizHistory.objects.create(
            user=self.user,
            quiz=self.quiz,
            game_id=game1,
            score=10,
            quiz_time=timezone.now().date()
        )

        QuizHistory.objects.create(
            user=user2,
            quiz=self.quiz,
            game_id=game1,
            score=20,
            quiz_time=timezone.now().date()
        )

        response = self.client.get(f"/api/quiz_history/{game1}/ranking/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(QuizHistory.objects.filter(game_id=game1)), 2)
        self.assertEqual(len(response.data["ranking"]), 2)