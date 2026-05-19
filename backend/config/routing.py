from applications.games.routing import websocket_urlpatterns as game_patterns
from applications.rooms.routing import websocket_urlpatterns as room_patterns


websocket_urlpatterns = [*room_patterns, *game_patterns]
