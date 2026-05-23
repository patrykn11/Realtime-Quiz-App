import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from rest_framework import status
from rest_framework.test import APIClient

from quizzes.models import Quiz
from rooms.consumers import RoomConsumer
from rooms.services import RoomService


def make_async_pipeline(execute_result=None):
    pipe = AsyncMock()
    pipe.execute = AsyncMock(return_value=execute_result)
    context = MagicMock()
    context.__aenter__.return_value = pipe
    context.__aexit__.return_value = None
    return context, pipe


class RoomApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test", password="pass")
        self.client.force_authenticate(user=self.user)
        Quiz.objects.create(name="sample_quiz")

    @patch("rooms.views.redis_client")
    @patch("rooms.views.random.choices")
    def test_create_room(self, mock_random, mock_redis):
        mock_redis.exists = MagicMock(return_value=False)
        mock_random.return_value = "ABC"

        response = self.client.post(
            "/api/create_room/",
            {"quiz_name": "sample_quiz"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        mock_redis.hset.assert_called_once_with(
            "room:ABC",
            mapping={
                "owner": "test",
                "status": "waiting",
                "quiz_name": "sample_quiz",
            },
        )

    def test_create_room_requires_authentication(self):
        response = APIClient().post(
            "/api/create_room/",
            {"quiz_name": "sample_quiz"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("rooms.views.redis_client")
    def test_create_room_rejects_unknown_quiz(self, mock_redis):
        response = self.client.post(
            "/api/create_room/",
            {"quiz_name": "unknown"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"error": "Quiz does not exist"})
        mock_redis.exists.assert_not_called()
        mock_redis.hset.assert_not_called()

    @patch("rooms.views.redis_client")
    @patch("rooms.views.random.choices")
    def test_create_room_retries_when_code_exists(self, mock_random, mock_redis):
        mock_random.side_effect = ["AAAAA", "BBBBB"]
        mock_redis.exists.side_effect = [True, False]

        response = self.client.post(
            "/api/create_room/",
            {"quiz_name": "sample_quiz"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"room_code": "BBBBB", "status": "ok"})
        self.assertEqual(
            mock_redis.exists.call_args_list,
            [call("room:AAAAA"), call("room:BBBBB")],
        )


class RoomServiceTests(SimpleTestCase):
    def test_get_keys(self):
        self.assertEqual(
            RoomService.get_keys("ABCDE"),
            ("room:ABCDE", "room:ABCDE:users"),
        )

    @patch("rooms.services.redis_client")
    def test_join_room_rejects_missing_room(self, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={})

        result = async_to_sync(RoomService.join_room)("ABCDE", "player")

        self.assertFalse(result)
        mock_redis.pipeline.assert_not_called()

    @patch("rooms.services.redis_client")
    def test_join_room_rejects_room_that_is_playing(self, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={"status": "playing"})

        result = async_to_sync(RoomService.join_room)("ABCDE", "player")

        self.assertFalse(result)

    @patch("rooms.services.redis_client")
    def test_join_room_adds_user_and_refreshes_ttls(self, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={"status": "waiting"})
        context, pipe = make_async_pipeline()
        mock_redis.pipeline = MagicMock(return_value=context)

        result = async_to_sync(RoomService.join_room)("ABCDE", "player")

        self.assertTrue(result)
        pipe.sadd.assert_awaited_once_with("room:ABCDE:users", "player")
        self.assertEqual(
            pipe.expire.await_args_list,
            [
                call("room:ABCDE", RoomService.ROOM_TTL),
                call("room:ABCDE:users", RoomService.ROOM_TTL),
            ],
        )
        pipe.execute.assert_awaited_once()

    @patch("rooms.services.redis_client")
    def test_leave_room_does_not_remove_player_during_game(self, mock_redis):
        mock_redis.hget = AsyncMock(return_value="playing")

        result = async_to_sync(RoomService.leave_room)("ABCDE", "player")

        self.assertTrue(result)
        mock_redis.pipeline.assert_not_called()

    @patch("rooms.services.redis_client")
    def test_leave_room_keeps_nonempty_room(self, mock_redis):
        mock_redis.hget = AsyncMock(return_value="waiting")
        context, pipe = make_async_pipeline([1, 2])
        mock_redis.pipeline = MagicMock(return_value=context)

        result = async_to_sync(RoomService.leave_room)("ABCDE", "player")

        self.assertTrue(result)
        pipe.srem.assert_awaited_once_with("room:ABCDE:users", "player")
        mock_redis.delete.assert_not_awaited()

    @patch("rooms.services.redis_client")
    def test_leave_room_deletes_empty_room(self, mock_redis):
        mock_redis.hget = AsyncMock(return_value="waiting")
        context, _ = make_async_pipeline([1, 0])
        mock_redis.pipeline = MagicMock(return_value=context)
        mock_redis.delete = AsyncMock()

        result = async_to_sync(RoomService.leave_room)("ABCDE", "player")

        self.assertFalse(result)
        mock_redis.delete.assert_awaited_once_with(
            "room:ABCDE", "room:ABCDE:users"
        )

    @patch("rooms.services.redis_client")
    def test_get_users_returns_list(self, mock_redis):
        mock_redis.smembers = AsyncMock(return_value={"anna", "bob"})

        result = async_to_sync(RoomService.get_users)("ABCDE")

        self.assertCountEqual(result, ["anna", "bob"])

    @patch("rooms.services.redis_client")
    def test_owner_can_start_game(self, mock_redis):
        mock_redis.hget = AsyncMock(return_value="owner")
        mock_redis.hset = AsyncMock()

        result = async_to_sync(RoomService.try_start_game)("ABCDE", "owner")

        self.assertTrue(result)
        mock_redis.hset.assert_awaited_once_with(
            "room:ABCDE", "status", "playing"
        )

    @patch("rooms.services.redis_client")
    def test_non_owner_cannot_start_game(self, mock_redis):
        mock_redis.hget = AsyncMock(return_value="owner")

        result = async_to_sync(RoomService.try_start_game)("ABCDE", "guest")

        self.assertFalse(result)
        mock_redis.hset.assert_not_awaited()


class RoomConsumerTests(SimpleTestCase):
    def make_consumer(self):
        consumer = RoomConsumer()
        consumer.room_code = "ABCDE"
        consumer.group_name = "room_ABCDE"
        consumer.user = SimpleNamespace(username="player", is_authenticated=True)
        consumer.channel_layer = MagicMock()
        consumer.channel_layer.group_send = AsyncMock()
        consumer.send = AsyncMock()
        return consumer

    def test_users_list_sends_serialized_event(self):
        consumer = self.make_consumer()
        event = {"type": "users_list", "users": ["anna", "bob"]}

        async_to_sync(consumer.users_list)(event)

        consumer.send.assert_awaited_once_with(text_data=json.dumps(event))

    def test_game_started_sends_serialized_event(self):
        consumer = self.make_consumer()
        event = {"type": "game_started"}

        async_to_sync(consumer.game_started)(event)

        consumer.send.assert_awaited_once_with(text_data=json.dumps(event))

    @patch("rooms.consumers.RoomService.try_start_game", new_callable=AsyncMock)
    def test_start_game_message_broadcasts_when_owner(self, mock_start):
        mock_start.return_value = True
        consumer = self.make_consumer()

        async_to_sync(consumer.receive)(json.dumps({"type": "start_game"}))

        consumer.channel_layer.group_send.assert_awaited_once_with(
            "room_ABCDE", {"type": "game_started"}
        )

    @patch("rooms.consumers.RoomService.try_start_game", new_callable=AsyncMock)
    def test_start_game_message_is_ignored_for_non_owner(self, mock_start):
        mock_start.return_value = False
        consumer = self.make_consumer()

        async_to_sync(consumer.receive)(json.dumps({"type": "start_game"}))

        consumer.channel_layer.group_send.assert_not_awaited()
