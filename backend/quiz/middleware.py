from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from jwt import decode as jwt_decode
from django.conf import settings
from urllib.parse import parse_qs

class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware for authenticating WebSocket connections using JWT tokens.
    If the token is missing or invalid, connection is closed.
    """
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token")

        if not token:
            await send({"type": "websocket.close", "code": 4401})
            return

        try:
            payload = jwt_decode(token[0], settings.SECRET_KEY, algorithms=["HS256"])
            User = get_user_model()
            scope["user"] = await User.objects.aget(id=payload["user_id"])
        except:
            await send({"type": "websocket.close", "code": 4401})
            return

        return await super().__call__(scope, receive, send)