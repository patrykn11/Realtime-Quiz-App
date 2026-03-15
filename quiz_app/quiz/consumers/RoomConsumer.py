from channels.generic.websocket import AsyncWebsocketConsumer
import json
import redis.asyncio as redis
from django.conf import settings

REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
redis_client = redis.from_url(REDIS_URL)

class RoomConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for quiz rooms.
    Manages user connections, user lists, and broadcasts updates to the room.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is opened.
        Adds user to Redis set for the room.
        Joins the user to the channel group and sends the current users list.
        """
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        room_exists = await redis_client.exists(f"room:{self.room_code}")
        if not room_exists:
            await self.close(code=4404)
            return

        self.group_name = f"room_{self.room_code}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        login = self.user.username
        await redis_client.sadd(f"room:{self.room_code}:users", login)
        users = await redis_client.smembers(f"room:{self.room_code}:users")
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "users_list", "users": [u.decode() for u in users]}
        )

    async def disconnect(self, close_code):
        """
        Called when a WebSocket connection is closed.
        Sends the updated users list or deletes the room if empty.
        """

        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

        login = self.user.username
        await redis_client.srem(f"room:{self.room_code}:users", login)

        users = await redis_client.smembers(f"room:{self.room_code}:users")

        if len(users) == 0:
            await redis_client.delete(f"room:{self.room_code}")
            await redis_client.delete(f"room:{self.room_code}:users")
        else:
            if hasattr(self, "group_name"):
                await self.channel_layer.group_send(
                    self.group_name,
                    {"type": "users_list", "users": [u.decode() for u in users]}
                )

    async def users_list(self, event):
        """
        Handler for broadcasting the users list to all clients in the room.
        """
        await self.send(text_data=json.dumps({"type": "users_list", "users": event["users"]}))