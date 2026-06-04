from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import CurrentUserAPIView, LoginAPIView, LogoutAPIView, RegisterUserAPIView


app_name = "users"
urlpatterns = [
    path("register/", RegisterUserAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", CurrentUserAPIView.as_view(), name="me"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
]
