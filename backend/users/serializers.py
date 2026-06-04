from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "date_joined")
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password_confirm")

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_email(self, value):
        value = User.objects.normalize_email(value).lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_refresh(self, value):
        try:
            token = RefreshToken(value)
        except TokenError as exc:
            raise serializers.ValidationError("Invalid or expired refresh token.") from exc

        user_id_claim = api_settings.USER_ID_CLAIM
        if str(token.get(user_id_claim)) != str(self.context["request"].user.pk):
            raise serializers.ValidationError("This refresh token belongs to another user.")

        self.token = token
        return value

    def save(self, **kwargs):
        try:
            self.token.blacklist()
        except TokenError as exc:
            raise serializers.ValidationError(
                {"refresh": "Invalid or expired refresh token."}
            ) from exc
