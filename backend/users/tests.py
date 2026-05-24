from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from jwt.exceptions import InvalidTokenError
from rest_framework import status
from rest_framework.test import APIClient

from users.middleware import JWTAuthMiddleware


class UserApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user_and_returns_tokens(self):
        response = self.client.post(
            "/api/register/",
            {"username": "new-user", "password": "strong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        user = get_user_model().objects.get(username="new-user")
        self.assertTrue(user.check_password("strong-password"))

    def test_register_rejects_missing_username(self):
        response = self.client.post(
            "/api/register/",
            {"password": "strong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "error"})

    def test_register_rejects_missing_password(self):
        response = self.client.post(
            "/api/register/",
            {"username": "new-user"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(get_user_model().objects.filter(username="new-user").exists())

    def test_register_rejects_duplicate_username(self):
        get_user_model().objects.create_user(
            username="existing-user",
            password="password",
        )

        response = self.client.post(
            "/api/register/",
            {"username": "existing-user", "password": "other-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"detail": "user exists"})
        self.assertEqual(
            get_user_model().objects.filter(username="existing-user").count(),
            1,
        )

    def test_login_returns_token_pair_for_valid_credentials(self):
        get_user_model().objects.create_user(
            username="player",
            password="password",
        )

        response = self.client.post(
            "/api/login/",
            {"username": "player", "password": "password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_rejects_invalid_credentials(self):
        get_user_model().objects.create_user(
            username="player",
            password="password",
        )

        response = self.client.post(
            "/api/login/",
            {"username": "player", "password": "wrong"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_endpoint_returns_new_access_token(self):
        registration = self.client.post(
            "/api/register/",
            {"username": "player", "password": "password"},
            format="json",
        )

        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": registration.data["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class JWTAuthMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.inner = AsyncMock()
        self.receive = AsyncMock()
        self.send = AsyncMock()
        self.middleware = JWTAuthMiddleware(self.inner)

    def test_missing_token_closes_connection(self):
        scope = {"query_string": b""}

        async_to_sync(self.middleware)(scope, self.receive, self.send)

        self.send.assert_awaited_once_with(
            {"type": "websocket.close", "code": 4401}
        )
        self.inner.assert_not_awaited()

    @patch("users.middleware.jwt_decode", side_effect=InvalidTokenError)
    def test_invalid_token_closes_connection(self, mock_decode):
        scope = {"query_string": b"token=invalid"}

        async_to_sync(self.middleware)(scope, self.receive, self.send)

        self.send.assert_awaited_once_with(
            {"type": "websocket.close", "code": 4401}
        )
        self.inner.assert_not_awaited()

    @patch("users.middleware.get_user_model")
    @patch("users.middleware.jwt_decode", return_value={"user_id": 7})
    def test_valid_token_adds_user_to_scope(self, mock_decode, mock_get_user_model):
        user = SimpleNamespace(id=7, username="player")
        user_model = MagicMock()
        user_model.DoesNotExist = type("DoesNotExist", (Exception,), {})
        user_model.objects.aget = AsyncMock(return_value=user)
        mock_get_user_model.return_value = user_model
        scope = {"query_string": b"token=valid"}

        async_to_sync(self.middleware)(scope, self.receive, self.send)

        self.assertIs(scope["user"], user)
        user_model.objects.aget.assert_awaited_once_with(id=7)
        self.inner.assert_awaited_once_with(scope, self.receive, self.send)
