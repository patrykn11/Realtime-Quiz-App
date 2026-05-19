from games.routing import websocket_urlpatterns as game_patterns
from rooms.routing import websocket_urlpatterns as room_patterns


websocket_urlpatterns = [*room_patterns, *game_patterns]
