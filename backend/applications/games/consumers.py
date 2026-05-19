import asyncio
import json
import time

from channels.generic.websocket import AsyncWebsocketConsumer

from .services import GameService


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.user = self.scope["user"]
        self.group_name = f"game_{self.room_code}"

        if not self.user.is_authenticated:
            await self.close(code=4001)
            return

        room_data, error = await GameService.get_initial_state(
            self.room_code, self.user.username
        )
        if error:
            error_codes = {
                "room_not_found": 4004,
                "not_a_member": 4006,
                "game_not_playing": 4005,
            }
            await self.close(code=error_codes.get(error, 4000))
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        self.owner = room_data.get("owner")
        self.quiz_name = await GameService.get_quiz_name(self.room_code)

        if room_data.get("is_run") == "true":
            await self.handle_reconnect()
        elif self.user.username == self.owner and room_data.get("is_run") != "end":
            asyncio.create_task(self.start_quiz_loop())

        if room_data.get("is_run") == "end":
            await self.send_final_score()

    async def handle_reconnect(self):
        question = await GameService.get_current_question(self.room_code)
        if question:
            remaining = GameService.QUESTION_TIME - (
                time.time() - float(question["start_time"])
            )
            if remaining > 0:
                await self.send_question_packet(
                    question["text"], question["answers"], round(remaining, 1)
                )

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "answer":
            await GameService.save_answer(
                self.room_code, self.user.username, data.get("answer")
            )

    async def start_quiz_loop(self):
        questions = await GameService.get_questions_by_quiz_name(self.quiz_name)
        await GameService.set_correct_answers(self.room_code, questions)

        for index, question in enumerate(questions):
            await GameService.set_current_question(self.room_code, index, question)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "broadcast_question",
                    "question": question["text"],
                    "answers": question["answers"],
                    "time_limit": GameService.QUESTION_TIME,
                },
            )
            await asyncio.sleep(GameService.QUESTION_TIME)
            results = await GameService.get_question_results(self.room_code, index)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "broadcast_question_results",
                    "correct_answer": results["correct_answer"],
                    "results": results["results"],
                },
            )
            await asyncio.sleep(2)

        await GameService.set_game_finished(self.room_code)
        await GameService.save_quiz(self.room_code, self.quiz_name)
        await self.send_scores_to_all()
        await self.channel_layer.group_send(
            self.group_name, {"type": "game_over_trigger"}
        )

    async def send_scores_to_all(self):
        ranking = await self.get_ranking()
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "broadcast_final_results", "ranking": ranking},
        )

    async def get_ranking(self):
        users = await GameService.get_users_in_room(self.room_code)
        return [
            {
                "username": username,
                "score": await GameService.get_score(
                    self.room_code, username, self.quiz_name
                ),
            }
            for username in users
        ]

    async def broadcast_final_results(self, event):
        ranking = event["ranking"]
        own_score = next(
            (
                entry["score"]
                for entry in ranking
                if entry["username"] == self.user.username
            ),
            0,
        )
        await self.send(
            text_data=json.dumps(
                {"type": "final_results", "ranking": ranking, "own_score": own_score}
            )
        )

    async def send_final_score(self):
        await self.broadcast_final_results({"ranking": await self.get_ranking()})

    async def broadcast_question(self, event):
        await self.send_question_packet(
            event["question"], event["answers"], event["time_limit"]
        )

    async def send_question_packet(self, text, answers, time_limit):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "question",
                    "question": text,
                    "answers": answers,
                    "time_limit": time_limit,
                }
            )
        )

    async def broadcast_question_results(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "question_results",
                    "correct_answer": event["correct_answer"],
                    "results": event["results"],
                }
            )
        )

    async def game_over_trigger(self, event):
        await self.send(text_data=json.dumps({"type": "game_over"}))
