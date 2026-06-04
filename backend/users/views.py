from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .services import create_token_pair


class RegisterUserAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                **create_token_pair(user),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer


class CurrentUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = LogoutSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
