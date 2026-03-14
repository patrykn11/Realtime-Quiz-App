from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import register_user, simple_endpoint

urlpatterns = [
    path("register/", register_user, name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),  # <--- standardowy
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("simple_endpoint/", simple_endpoint, name="simple_endpoint")
]