from channels.generic.websocket import AsyncWebsocketConsumer
import json
import redis.asyncio as redis
from django.conf import settings
import asyncio


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

        curr_status = await redis_client.hget(f"room:{self.room_code}", "status")  
        if curr_status:
            curr_status = curr_status.decode()      
        if curr_status != "playing":
            await self.close(code=4005)
            return

        self.group_name = f"game_{self.room_code}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        

        current_question = await redis_client.hget(
            f"room:{self.room_code}",
            "current_question"
        )
        if not current_question:
            current_question = "0"
        else:
            current_question.decode()
        print("ASFIUHSAIUHFUHISDFSDF", current_question)

        if current_question:
            idx = int(current_question)

            questions = [
                {"text": "Jakie jest stolica Polski?", "answers": ["Warszawa", "Kraków"]},
                {"text": "2 + 2 = ?", "answers": ["3", "4"]},
                {"text": "Jaki kolor ma niebo?", "answers": ["Niebieski", "Zielony"]}
            ]

            if idx < len(questions):
                question = questions[idx]
                print("sndfhdsfsdufhshdfhusdfhu")

                await self.send(text_data=json.dumps({
                    "type": "question",
                    "question": question["text"],
                    "answers": question["answers"]
                }))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

        
    async def receive(self, text_data):
        if text_data:
            data = json.loads(text_data)
            if data.get("type") == "answer":
                ans = data.get("answer")
                if ans == "1":
                    score = await redis_client.hget(f"room:{self.room_code}:{self.user.username}", "ans")
                    score_int = int(score.decode()) if score else 0
                    await redis_client.hset(f"room:{self.room_code}:{self.user.username}", "ans", score_int + 1)

    async def start_quiz(self, event):
        print("GAME CONSUMER")
        self.room_code = event.get("room_code")
        self.group_name = f"game_{self.room_code}"
        questions = [
            {"text": "Jakie jest stolica Polski?", "answers": ["Warszawa", "Kraków"]},
            {"text": "2 + 2 = ?", "answers": ["3", "4"]},
            {"text": "Jaki kolor ma niebo?", "answers": ["Niebieski", "Zielony"]}
        ]
        
        for idx, question in enumerate(questions):
            await redis_client.hset(f"room:{self.room_code}", "current_question", idx)
            await self.channel_layer.group_send(self.group_name,
            {
                "type": "send_question",
                "question": question["text"],
                "answers": question["answers"]
            })
            await asyncio.sleep(1)


                
    async def send_question(self, event):

        await self.send(text_data=json.dumps({
            "type": "question",
            "question": event["question"],
            "answers": event["answers"]
        }))
        

