from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import register_user, simple_endpoint, create_room, quizes_name_list, create_quiz

urlpatterns = [
    path("register/", register_user, name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("simple_endpoint/", simple_endpoint, name="simple_endpoint"),
    path("create_room/", create_room, name="create_room"),
    path("quizes_name/", quizes_name_list, name="quizes_name"),
    path("create_quiz/", create_quiz, name="create_quiz")
]