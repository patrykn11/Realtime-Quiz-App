import uuid
from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from histories.models import QuizHistory
from histories.serializers import (
    QuizHistoryRankingEntrySerializer,
    QuizHistorySerializer,
    UserStatsPerDaySerializer,
)
from quizzes.models import Quiz


class QuizHistoryModelAndSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="player", password="pass")
        self.quiz = Quiz.objects.create(name="History Quiz")
        self.history = QuizHistory.objects.create(
            user=self.user,
            quiz=self.quiz,
            score=5,
        )

    def test_history_string_representation(self):
        self.assertEqual(str(self.history), "player - History Quiz - 5")

    def test_game_id_is_generated_and_indexed(self):
        other = QuizHistory.objects.create(user=self.user, quiz=self.quiz, score=1)

        self.assertIsInstance(self.history.game_id, uuid.UUID)
        self.assertNotEqual(self.history.game_id, other.game_id)
        self.assertTrue(QuizHistory._meta.get_field("game_id").db_index)

    def test_deleting_user_deletes_history(self):
        history_id = self.history.id

        self.user.delete()

        self.assertFalse(QuizHistory.objects.filter(id=history_id).exists())

    def test_quiz_history_serializer_uses_public_field_names(self):
        data = QuizHistorySerializer(self.history).data

        self.assertEqual(data["quiz_name"], "History Quiz")
        self.assertEqual(data["score"], 5)
        self.assertEqual(data["created_at"], str(self.history.quiz_time))

    def test_ranking_entry_converts_null_score_to_zero(self):
        self.history.score = None

        data = QuizHistoryRankingEntrySerializer(self.history).data

        self.assertEqual(data, {"username": "player", "score": 0})

    def test_daily_serializer_maps_annotated_fields(self):
        data = UserStatsPerDaySerializer(
            {"quiz_time": date(2026, 5, 19), "count": 3}
        ).data

        self.assertEqual(data, {"date": "2026-05-19", "quizzes_played": 3})


class StatsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test", password="pass")
        self.client.force_authenticate(user=self.user)
        self.quiz = Quiz.objects.create(name="sample_quiz")

    def create_history(self, *, user=None, score=1, game_id=None, quiz_date=None):
        history = QuizHistory.objects.create(
            user=user or self.user,
            quiz=self.quiz,
            score=score,
            **({"game_id": game_id} if game_id else {}),
        )
        if quiz_date:
            QuizHistory.objects.filter(id=history.id).update(quiz_time=quiz_date)
            history.refresh_from_db()
        return history

    def test_user_stats(self):
        self.create_history(score=10)

        response = self.client.get("/api/user_stats/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_user_stats_requires_authentication(self):
        response = APIClient().get("/api/user_stats/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_stats_contains_only_requesting_users_histories(self):
        other_user = User.objects.create_user(username="other", password="pass")
        self.create_history(score=10)
        self.create_history(user=other_user, score=20)

        response = self.client.get("/api/user_stats/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["score"], 10)

    def test_user_stats_orders_newest_history_first(self):
        older = self.create_history(score=1, quiz_date=date(2026, 5, 18))
        newer = self.create_history(score=2, quiz_date=date(2026, 5, 19))

        response = self.client.get("/api/user_stats/")

        self.assertEqual(
            [item["id"] for item in response.data],
            [newer.id, older.id],
        )

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

    def test_user_stats_per_day_groups_and_orders_dates(self):
        self.create_history(score=1, quiz_date=date(2026, 5, 20))
        self.create_history(score=2, quiz_date=date(2026, 5, 19))
        self.create_history(score=3, quiz_date=date(2026, 5, 19))

        response = self.client.get("/api/user_stats_per_day/")

        self.assertEqual(
            response.data,
            [
                {"date": "2026-05-19", "quizzes_played": 2},
                {"date": "2026-05-20", "quizzes_played": 1},
            ],
        )

    def test_user_stats_per_day_requires_authentication(self):
        response = APIClient().get("/api/user_stats_per_day/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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

    def test_ranking_orders_scores_descending_then_usernames(self):
        game_id = uuid.uuid4()
        anna = User.objects.create_user(username="anna", password="pass")
        bob = User.objects.create_user(username="bob", password="pass")
        self.create_history(score=5, game_id=game_id)
        self.create_history(user=bob, score=10, game_id=game_id)
        self.create_history(user=anna, score=10, game_id=game_id)

        response = self.client.get(f"/api/quiz_history/{game_id}/ranking/")

        self.assertEqual(
            response.data["ranking"],
            [
                {"username": "anna", "score": 10},
                {"username": "bob", "score": 10},
                {"username": "test", "score": 5},
            ],
        )

    def test_ranking_returns_404_when_user_did_not_play_game(self):
        other = User.objects.create_user(username="other", password="pass")
        game_id = uuid.uuid4()
        self.create_history(user=other, score=10, game_id=game_id)

        response = self.client.get(f"/api/quiz_history/{game_id}/ranking/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"detail": "history not found"})

    def test_ranking_requires_authentication(self):
        response = APIClient().get(
            f"/api/quiz_history/{uuid.uuid4()}/ranking/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
