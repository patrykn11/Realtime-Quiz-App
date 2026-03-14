from channels.generic.websocket import AsyncWebsocketConsumer
import json
import redis.asyncio as redis
from django.conf import settings
REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
redis_client = redis.from_url(REDIS_URL)
class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close(code=4401)
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
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        login = self.user.username
        await redis_client.srem(f"room:{self.room_code}:users", login)
        users = await redis_client.smembers(f"room:{self.room_code}:users")
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "users_list", "users": [u.decode() for u in users]}
        )

    async def users_list(self, event):
        await self.send(text_data=json.dumps({"type": "users_list", "users": event["users"]}))