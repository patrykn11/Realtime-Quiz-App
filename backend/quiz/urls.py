from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    CreateQuizAPIView,
    CreateRoomAPIView,
    QuizHistoryRankingAPIView,
    QuizesNameListAPIView,
    RegisterUserAPIView,
    UserStatsAPIView,
    UserStatsPerDayAPIView,
)

urlpatterns = [
    path("register/", RegisterUserAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("create_room/", CreateRoomAPIView.as_view(), name="create_room"),
    path("quizes_name/", QuizesNameListAPIView.as_view(), name="quizes_name"),
    path("create_quiz/", CreateQuizAPIView.as_view(), name="create_quiz"),
    path("user_stats/", UserStatsAPIView.as_view(), name="user_stats"),
    path(
        "user_stats_per_day/",
        UserStatsPerDayAPIView.as_view(),
        name="user_stats_per_day",
    ),
    path(
        "quiz_history/<uuid:game_id>/ranking/",
        QuizHistoryRankingAPIView.as_view(),
        name="quiz_history_ranking",
    ),
]
