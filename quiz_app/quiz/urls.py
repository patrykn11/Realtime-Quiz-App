from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import register_user, create_room, quizes_name_list, create_quiz, user_stats, user_stats_per_day, quiz_history_ranking

urlpatterns = [
    path("register/", register_user, name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("create_room/", create_room, name="create_room"),
    path("quizes_name/", quizes_name_list, name="quizes_name"),
    path("create_quiz/", create_quiz, name="create_quiz"),
    path("user_stats/", user_stats, name="user_stats"),
    path("user_stats_per_day/", user_stats_per_day, name="user_stats_per_day"),
    path("quiz_history/<int:history_id>/ranking/", quiz_history_ranking, name="quiz_history_ranking")
]
