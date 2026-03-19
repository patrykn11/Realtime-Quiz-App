import json
from channels.generic.websocket import AsyncWebsocketConsumer
from ..services.RoomService import RoomService


class RoomConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for managing a room.
    Handles joining, leaving, and broadcasting user list.
    """

    async def connect(self):
        """Handle new WebSocket connection and attempt to join room."""
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.user = self.scope["user"]
        self.group_name = f"room_{self.room_code}"

        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        joined = await RoomService.join_room(self.room_code, self.user.username)
        if not joined:
            await self.close(code=4404)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.broadcast_user_list()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection and leave room."""
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            room_still_exists = await RoomService.leave_room(self.room_code, self.user.username)
            if room_still_exists:
                await self.broadcast_user_list()

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        data = json.loads(text_data)
        if data.get("type") == "start_game":
            if await RoomService.try_start_game(self.room_code, self.user.username):
                await self.channel_layer.group_send(
                    self.group_name, {"type": "game_started"}
                )

    async def broadcast_user_list(self):
        """Broadcast the current list of users in the room."""
        users = await RoomService.get_users(self.room_code)
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "users_list", "users": users}
        )

    async def users_list(self, event):
        """Send updated user list to WebSocket client."""
        await self.send(text_data=json.dumps(event))

    async def game_started(self, event):
        """Notify clients that the game has started."""
        await self.send(text_data=json.dumps(event))