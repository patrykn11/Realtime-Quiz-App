from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    path("ws/room/<str:room_code>/", consumers.RoomConsumer.as_asgi()),
    path("ws/game/<str:room_code>/", consumers.GameConsumer.as_asgi()),
]