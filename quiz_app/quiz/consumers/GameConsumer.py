from channels.generic.websocket import AsyncWebsocketConsumer
import json
import redis.asyncio as redis
from django.conf import settings

REDIS_URL = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
redis_client = redis.from_url(REDIS_URL)

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        room_exists = await redis_client.exists(f"room:{self.room_code}")
        if not room_exists:
            await self.close(code=4004)
            return
        
        self.group_name = f"game:{self.room_code}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept

        curr_status = await redis_client.hget(f"room:{self.room_code}", "status")  
        if curr_status:
            curr_status = curr_status.decode()      
        if not curr_status != "playing":
            await self.close(code=4005)
            return

        self.group_name = f"game_{self.room_code}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        
    async def disconnect(self):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

        

