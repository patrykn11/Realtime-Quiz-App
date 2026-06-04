from urllib.parse import parse_qs

from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, TokenError


class JWTAuthMiddleware(BaseMiddleware):
    """Authenticate a WebSocket connection using a JWT query parameter."""

    async def __call__(self, scope, receive, send):
        token = parse_qs(scope["query_string"].decode()).get("token")
        if not token:
            await send({"type": "websocket.close", "code": 4401})
            return

        user_model = get_user_model()
        try:
            access_token = AccessToken(token[0])
            user = await user_model.objects.aget(
                id=access_token[api_settings.USER_ID_CLAIM],
                is_active=True,
            )
            scope["user"] = user
        except (TokenError, KeyError, user_model.DoesNotExist, ValueError):
            await send({"type": "websocket.close", "code": 4401})
            return

        return await super().__call__(scope, receive, send)
