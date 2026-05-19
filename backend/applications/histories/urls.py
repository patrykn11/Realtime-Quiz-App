from django.urls import path

from .views import QuizHistoryRankingAPIView, UserStatsAPIView, UserStatsPerDayAPIView


app_name = "histories"
urlpatterns = [
    path("user_stats/", UserStatsAPIView.as_view(), name="user-stats"),
    path("user_stats_per_day/", UserStatsPerDayAPIView.as_view(), name="stats-per-day"),
    path(
        "quiz_history/<uuid:game_id>/ranking/",
        QuizHistoryRankingAPIView.as_view(),
        name="ranking",
    ),
]
