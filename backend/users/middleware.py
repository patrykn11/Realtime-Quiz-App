from urllib.parse import parse_qs

from channels.middleware import BaseMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import decode as jwt_decode
from jwt.exceptions import InvalidTokenError


class JWTAuthMiddleware(BaseMiddleware):
    """Authenticate a WebSocket connection using a JWT query parameter."""

    async def __call__(self, scope, receive, send):
        token = parse_qs(scope["query_string"].decode()).get("token")
        if not token:
            await send({"type": "websocket.close", "code": 4401})
            return

        user_model = get_user_model()
        try:
            payload = jwt_decode(token[0], settings.SECRET_KEY, algorithms=["HS256"])
            scope["user"] = await user_model.objects.aget(id=payload["user_id"])
        except (InvalidTokenError, KeyError, user_model.DoesNotExist, ValueError):
            await send({"type": "websocket.close", "code": 4401})
            return

        return await super().__call__(scope, receive, send)
