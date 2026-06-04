from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import TokenError

from users.middleware import JWTAuthMiddleware


User = get_user_model()


class UserApiTests(TestCase):
    password = "Strong-password-123!"

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")
        self.refresh_url = reverse("users:token-refresh")
        self.me_url = reverse("users:me")
        self.logout_url = reverse("users:logout")

    def create_user(self, username="player", email="player@example.com", **kwargs):
        return User.objects.create_user(
            username=username,
            email=email,
            password=self.password,
            **kwargs,
        )

    def register(self, **overrides):
        payload = {
            "username": "new-player",
            "email": "player@example.com",
            "password": self.password,
            "password_confirm": self.password,
        }
        payload.update(overrides)
        return self.client.post(self.register_url, payload, format="json")

    def login(self, username="player", password=None):
        return self.client.post(
            self.login_url,
            {"username": username, "password": password or self.password},
            format="json",
        )

    def authenticate(self, access):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_project_uses_custom_user_model(self):
        self.assertEqual(User._meta.label, "users.User")

    def test_register_creates_user_and_returns_user_with_token_pair(self):
        response = self.register(email="PLAYER@Example.COM")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "new-player")
        self.assertNotIn("password", response.data["user"])

        user = User.objects.get(username="new-player")
        self.assertEqual(user.email, "player@example.com")
        self.assertTrue(user.check_password(self.password))

    def test_register_requires_every_field(self):
        for missing_field in ("username", "email", "password", "password_confirm"):
            with self.subTest(missing_field=missing_field):
                payload = {
                    "username": "new-player",
                    "email": "player@example.com",
                    "password": self.password,
                    "password_confirm": self.password,
                }
                payload.pop(missing_field)
                response = self.client.post(self.register_url, payload, format="json")

                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(missing_field, response.data)

    def test_register_rejects_password_mismatch(self):
        response = self.register(password_confirm="Different-password-123!")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)
        self.assertFalse(User.objects.exists())

    def test_register_accepts_short_numeric_password(self):
        response = self.register(password="123", password_confirm="123")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.get(username="new-player").check_password("123"))

    def test_register_accepts_password_identical_to_username(self):
        response = self.register(
            username="same-as-password",
            password="same-as-password",
            password_confirm="same-as-password",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.get(username="same-as-password").check_password(
                "same-as-password"
            )
        )

    def test_register_rejects_username_case_insensitively(self):
        self.create_user(username="Existing")

        response = self.register(username="existing", email="other@example.com")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_rejects_email_case_insensitively(self):
        self.create_user(email="existing@example.com")

        response = self.register(email="EXISTING@example.com")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_login_returns_token_pair_and_serialized_user(self):
        user = self.create_user()

        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["id"], user.id)
        self.assertEqual(response.data["user"]["email"], user.email)

    def test_login_rejects_invalid_credentials(self):
        self.create_user()

        response = self.login(password="wrong-password")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access", response.data)

    def test_login_rejects_inactive_user(self):
        self.create_user(is_active=False)

        response = self.login()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_authenticated_user(self):
        user = self.create_user()
        tokens = self.login().data
        self.authenticate(tokens["access"])

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], user.id)
        self.assertEqual(response.data["username"], user.username)

    def test_me_requires_authentication(self):
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rotates_token_and_blacklists_previous_token(self):
        self.create_user()
        original_refresh = self.login().data["refresh"]

        response = self.client.post(
            self.refresh_url,
            {"refresh": original_refresh},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertNotEqual(response.data["refresh"], original_refresh)

        replay = self.client.post(
            self.refresh_url,
            {"refresh": original_refresh},
            format="json",
        )
        self.assertEqual(replay.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_rejects_invalid_token(self):
        response = self.client.post(
            self.refresh_url,
            {"refresh": "not-a-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_blacklists_refresh_token(self):
        self.create_user()
        tokens = self.login().data
        self.authenticate(tokens["access"])

        response = self.client.post(
            self.logout_url,
            {"refresh": tokens["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": tokens["refresh"]},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_requires_access_token(self):
        self.create_user()
        refresh = self.login().data["refresh"]
        self.client.credentials()

        response = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_rejects_another_users_refresh_token(self):
        self.create_user()
        first_tokens = self.login().data
        self.create_user(username="other", email="other@example.com")
        other_tokens = self.login(username="other").data
        self.authenticate(first_tokens["access"])

        response = self.client.post(
            self.logout_url,
            {"refresh": other_tokens["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)

    def test_logout_rejects_invalid_refresh_token(self):
        self.create_user()
        access = self.login().data["access"]
        self.authenticate(access)

        response = self.client.post(
            self.logout_url,
            {"refresh": "not-a-token"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh", response.data)


class JWTAuthMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.inner = AsyncMock()
        self.receive = AsyncMock()
        self.send = AsyncMock()
        self.middleware = JWTAuthMiddleware(self.inner)

    def test_missing_token_closes_connection(self):
        scope = {"query_string": b""}
        async_to_sync(self.middleware)(scope, self.receive, self.send)

        self.send.assert_awaited_once_with({"type": "websocket.close", "code": 4401})
        self.inner.assert_not_awaited()

    @patch("users.middleware.AccessToken", side_effect=TokenError("invalid token"))
    def test_invalid_token_closes_connection(self, mock_access_token):
        scope = {"query_string": b"token=invalid"}
        async_to_sync(self.middleware)(scope, self.receive, self.send)

        mock_access_token.assert_called_once_with("invalid")
        self.send.assert_awaited_once_with({"type": "websocket.close", "code": 4401})
        self.inner.assert_not_awaited()

    @patch("users.middleware.get_user_model")
    @patch("users.middleware.AccessToken")
    def test_valid_token_adds_active_user_to_scope(self, mock_access_token, mock_get_user_model):
        user = SimpleNamespace(id=7, username="player", is_active=True)
        parsed_token = MagicMock()
        parsed_token.__getitem__.return_value = 7
        mock_access_token.return_value = parsed_token
        user_model = MagicMock()
        user_model.DoesNotExist = type("DoesNotExist", (Exception,), {})
        user_model.objects.aget = AsyncMock(return_value=user)
        mock_get_user_model.return_value = user_model
        scope = {"query_string": b"token=valid"}

        async_to_sync(self.middleware)(scope, self.receive, self.send)

        self.assertIs(scope["user"], user)
        user_model.objects.aget.assert_awaited_once_with(id=7, is_active=True)
        self.inner.assert_awaited_once_with(scope, self.receive, self.send)

    @patch("users.middleware.get_user_model")
    @patch("users.middleware.AccessToken")
    def test_missing_or_inactive_user_closes_connection(self, mock_access_token, mock_get_user_model):
        parsed_token = MagicMock()
        parsed_token.__getitem__.return_value = 7
        mock_access_token.return_value = parsed_token
        user_model = MagicMock()
        user_model.DoesNotExist = type("DoesNotExist", (Exception,), {})
        user_model.objects.aget = AsyncMock(side_effect=user_model.DoesNotExist)
        mock_get_user_model.return_value = user_model

        async_to_sync(self.middleware)(
            {"query_string": b"token=valid"},
            self.receive,
            self.send,
        )

        self.send.assert_awaited_once_with({"type": "websocket.close", "code": 4401})
        self.inner.assert_not_awaited()
