import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

django_asgi_application = get_asgi_application()

from applications.users.middleware import JWTAuthMiddleware
from config.routing import websocket_urlpatterns


application = ProtocolTypeRouter(
    {
        "http": django_asgi_application,
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
