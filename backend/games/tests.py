import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from choices.models import Choice
from games.consumers import GameConsumer
from games.services import GameService
from histories.models import QuizHistory
from questions.models import Question
from quizzes.models import Quiz


def make_async_pipeline():
    pipe = AsyncMock()
    context = MagicMock()
    context.__aenter__.return_value = pipe
    context.__aexit__.return_value = None
    return context, pipe


class GameServiceTest(TestCase):
    def setUp(self):
        quiz = Quiz.objects.create(name="sample")
        question = Question.objects.create(quiz=quiz, text="2+2")
        Choice.objects.create(question=question, text="3", is_correct=False)
        Choice.objects.create(question=question, text="4", is_correct=True)

    def test_get_keys(self):
        room_key, users_key, answers_key = GameService.get_keys("room1", "john")

        self.assertEqual(room_key, "room:room1")
        self.assertEqual(users_key, "room:room1:users")
        self.assertEqual(answers_key, "game:room1:john")

    def test_get_keys_without_username_has_no_answers_key(self):
        _, _, answers_key = GameService.get_keys("room1")

        self.assertIsNone(answers_key)

    def test_correct_answers_key(self):
        self.assertEqual(
            GameService.get_correct_answers_key("room1"),
            "game:room1:correct_answers",
        )

    def test_get_questions_by_quiz(self):
        result = async_to_sync(GameService.get_questions_by_quiz_name)("sample")

        self.assertEqual(result[0]["answers"], ["3", "4"])
        self.assertEqual(result[0]["correct_ans"], 1)

    def test_get_questions_returns_empty_list_for_unknown_quiz(self):
        result = async_to_sync(GameService.get_questions_by_quiz_name)("unknown")

        self.assertEqual(result, [])

    @patch("games.services.redis_client")
    def test_get_initial_state_rejects_missing_room(self, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={})

        state, error = async_to_sync(GameService.get_initial_state)(
            "room1", "john"
        )

        self.assertIsNone(state)
        self.assertEqual(error, "room_not_found")

    @patch("games.services.redis_client")
    def test_get_initial_state_rejects_non_member(self, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={"status": "playing"})
        mock_redis.sismember = AsyncMock(return_value=False)

        state, error = async_to_sync(GameService.get_initial_state)(
            "room1", "john"
        )

        self.assertIsNone(state)
        self.assertEqual(error, "not_a_member")

    @patch("games.services.redis_client")
    def test_get_initial_state_rejects_waiting_game(self, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={"status": "waiting"})
        mock_redis.sismember = AsyncMock(return_value=True)

        state, error = async_to_sync(GameService.get_initial_state)(
            "room1", "john"
        )

        self.assertIsNone(state)
        self.assertEqual(error, "game_not_playing")

    @patch("games.services.redis_client")
    def test_get_initial_state_returns_playing_room(self, mock_redis):
        room = {"status": "playing", "owner": "john"}
        mock_redis.hgetall = AsyncMock(return_value=room)
        mock_redis.sismember = AsyncMock(return_value=True)

        state, error = async_to_sync(GameService.get_initial_state)(
            "room1", "john"
        )

        self.assertEqual(state, room)
        self.assertIsNone(error)

    @patch("games.services.redis_client")
    def test_get_score(self, mock_redis):
        mock_redis.hgetall = AsyncMock(side_effect=[{"0": "1"}, {"0": "1"}])

        score = async_to_sync(GameService.get_score)("room1", "john", "sample")

        self.assertEqual(score, 1)

    @patch("games.services.redis_client")
    def test_get_score_returns_zero_without_answers(self, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={})

        score = async_to_sync(GameService.get_score)("room1", "john", "sample")

        self.assertEqual(score, 0)

    @patch.object(
        GameService,
        "get_questions_by_quiz_name",
        new_callable=AsyncMock,
    )
    @patch("games.services.redis_client")
    def test_get_score_falls_back_to_database_answers(
        self, mock_redis, mock_questions
    ):
        mock_redis.hgetall = AsyncMock(side_effect=[{"0": "1"}, {}])
        mock_questions.return_value = [{"correct_ans": 1}]

        score = async_to_sync(GameService.get_score)("room1", "john", "sample")

        self.assertEqual(score, 1)
        mock_questions.assert_awaited_once_with("sample")

    @patch("games.services.redis_client")
    def test_get_score_ignores_invalid_answer_value(self, mock_redis):
        mock_redis.hgetall = AsyncMock(
            side_effect=[{"0": "not-a-number"}, {"0": "1"}]
        )

        score = async_to_sync(GameService.get_score)("room1", "john", "sample")

        self.assertEqual(score, 0)

    @patch("games.services.redis_client")
    def test_get_current_question(self, mock_redis):
        mock_redis.hgetall = AsyncMock(
            return_value={
                "current_question_text": "2+2",
                "current_question_answers": '["3", "4"]',
                "start_time": "123",
            }
        )

        result = async_to_sync(GameService.get_current_question)("room1")

        self.assertEqual(result["text"], "2+2")
        self.assertEqual(result["answers"], ["3", "4"])

    @patch("games.services.redis_client")
    def test_get_current_question_returns_none_without_question(self, mock_redis):
        mock_redis.hgetall = AsyncMock(return_value={"status": "playing"})

        result = async_to_sync(GameService.get_current_question)("room1")

        self.assertIsNone(result)

    @patch("games.services.redis_client")
    def test_save_answer(self, mock_redis):
        mock_redis.hget = AsyncMock(return_value="0")
        mock_pipe = AsyncMock()
        mock_context = MagicMock()
        mock_context.__aenter__.return_value = mock_pipe
        mock_context.__aexit__.return_value = None
        mock_redis.pipeline = MagicMock(return_value=mock_context)

        result = async_to_sync(GameService.save_answer)("room1", "john", 1)

        self.assertTrue(result)
        mock_pipe.hset.assert_awaited_once_with("game:room1:john", "0", "1")
        mock_pipe.expire.assert_awaited_once_with(
            "game:room1:john", GameService.ROOM_TTL
        )
        mock_pipe.execute.assert_awaited_once()

    @patch("games.services.redis_client")
    def test_save_answer_returns_false_without_current_question(self, mock_redis):
        mock_redis.hget = AsyncMock(return_value=None)

        result = async_to_sync(GameService.save_answer)("room1", "john", 1)

        self.assertFalse(result)
        mock_redis.pipeline.assert_not_called()

    @patch("games.services.redis_client")
    def test_set_correct_answers_ignores_empty_questions(self, mock_redis):
        async_to_sync(GameService.set_correct_answers)("room1", [])

        mock_redis.pipeline.assert_not_called()

    @patch("games.services.redis_client")
    def test_set_correct_answers_replaces_mapping_and_sets_ttl(self, mock_redis):
        context, pipe = make_async_pipeline()
        mock_redis.pipeline = MagicMock(return_value=context)

        async_to_sync(GameService.set_correct_answers)(
            "room1",
            [{"correct_ans": 1}, {"correct_ans": 0}],
        )

        pipe.delete.assert_awaited_once_with("game:room1:correct_answers")
        pipe.hset.assert_awaited_once_with(
            "game:room1:correct_answers",
            mapping={"0": "1", "1": "0"},
        )
        pipe.expire.assert_awaited_once_with(
            "game:room1:correct_answers", GameService.ROOM_TTL
        )
        pipe.execute.assert_awaited_once()

    @patch("games.services.time.time", return_value=123.5)
    @patch("games.services.redis_client")
    def test_set_current_question_stores_reconnect_state(self, mock_redis, mock_time):
        context, pipe = make_async_pipeline()
        mock_redis.pipeline = MagicMock(return_value=context)

        async_to_sync(GameService.set_current_question)(
            "room1",
            2,
            {"text": "2+2", "answers": ["3", "4"]},
        )

        pipe.hset.assert_awaited_once_with(
            "room:room1",
            mapping={
                "current_question": 2,
                "current_question_text": "2+2",
                "current_question_answers": '["3", "4"]',
                "start_time": "123.5",
                "is_run": "true",
            },
        )
        pipe.expire.assert_awaited_once_with("room:room1", GameService.ROOM_TTL)

    @patch("games.services.redis_client")
    def test_set_game_finished_marks_room_as_ended(self, mock_redis):
        mock_redis.hset = AsyncMock()

        async_to_sync(GameService.set_game_finished)("room1")

        mock_redis.hset.assert_awaited_once_with("room:room1", "is_run", "end")

    @patch("games.services.redis_client")
    def test_get_question_results_returns_sorted_results(self, mock_redis):
        mock_redis.hget = AsyncMock(side_effect=["1", "0", "1"])
        mock_redis.smembers = AsyncMock(return_value=["bob", "anna"])

        result = async_to_sync(GameService.get_question_results)("room1", 0)

        self.assertEqual(result["correct_answer"], 1)
        self.assertEqual(
            result["results"],
            [
                {"username": "anna", "answer": 1, "is_correct": True},
                {"username": "bob", "answer": 0, "is_correct": False},
            ],
        )

    @patch("games.services.redis_client")
    def test_get_question_results_handles_missing_correct_answer(self, mock_redis):
        mock_redis.hget = AsyncMock(side_effect=[None, None])
        mock_redis.smembers = AsyncMock(return_value=["anna"])

        result = async_to_sync(GameService.get_question_results)("room1", 0)

        self.assertIsNone(result["correct_answer"])
        self.assertEqual(
            result["results"],
            [{"username": "anna", "answer": None, "is_correct": False}],
        )

    @patch("games.services.redis_client")
    def test_get_quiz_name_reads_room_hash(self, mock_redis):
        mock_redis.hget = AsyncMock(return_value="sample")

        result = async_to_sync(GameService.get_quiz_name)("room1")

        self.assertEqual(result, "sample")
        mock_redis.hget.assert_awaited_once_with("room:room1", "quiz_name")

    @patch("games.services.redis_client")
    def test_get_users_in_room(self, mock_redis):
        mock_redis.smembers = AsyncMock(return_value={"john", "anna"})

        result = async_to_sync(GameService.get_users_in_room)("room1")

        self.assertIn("john", result)
        self.assertIn("anna", result)

    @patch.object(GameService, "get_score", new_callable=AsyncMock)
    @patch.object(GameService, "get_users_in_room", new_callable=AsyncMock)
    def test_save_quiz_creates_history_for_every_player(
        self, mock_users, mock_score
    ):
        User.objects.create_user(username="john", password="pass")
        User.objects.create_user(username="anna", password="pass")
        mock_users.return_value = ["john", "anna"]
        mock_score.side_effect = [2, 1]

        async_to_sync(GameService.save_quiz)("room1", "sample")

        histories = list(QuizHistory.objects.order_by("user__username"))
        self.assertEqual(len(histories), 2)
        self.assertEqual([history.score for history in histories], [1, 2])
        self.assertEqual(histories[0].game_id, histories[1].game_id)


class GameConsumerTests(SimpleTestCase):
    def make_consumer(self):
        consumer = GameConsumer()
        consumer.room_code = "room1"
        consumer.group_name = "game_room1"
        consumer.quiz_name = "sample"
        consumer.user = SimpleNamespace(username="john", is_authenticated=True)
        consumer.channel_layer = MagicMock()
        consumer.channel_layer.group_send = AsyncMock()
        consumer.send = AsyncMock()
        return consumer

    @patch("games.consumers.GameService.save_answer", new_callable=AsyncMock)
    def test_receive_saves_answer_message(self, mock_save_answer):
        consumer = self.make_consumer()

        async_to_sync(consumer.receive)(
            json.dumps({"type": "answer", "answer": 2})
        )

        mock_save_answer.assert_awaited_once_with("room1", "john", 2)

    @patch("games.consumers.GameService.save_answer", new_callable=AsyncMock)
    def test_receive_ignores_unrelated_message(self, mock_save_answer):
        consumer = self.make_consumer()

        async_to_sync(consumer.receive)(json.dumps({"type": "ping"}))

        mock_save_answer.assert_not_awaited()

    def test_send_question_packet_serializes_payload(self):
        consumer = self.make_consumer()

        async_to_sync(consumer.send_question_packet)("2+2", ["3", "4"], 3)

        payload = json.loads(consumer.send.await_args.kwargs["text_data"])
        self.assertEqual(
            payload,
            {
                "type": "question",
                "question": "2+2",
                "answers": ["3", "4"],
                "time_limit": 3,
            },
        )

    def test_broadcast_final_results_includes_own_score(self):
        consumer = self.make_consumer()
        ranking = [
            {"username": "anna", "score": 2},
            {"username": "john", "score": 1},
        ]

        async_to_sync(consumer.broadcast_final_results)({"ranking": ranking})

        payload = json.loads(consumer.send.await_args.kwargs["text_data"])
        self.assertEqual(payload["own_score"], 1)
        self.assertEqual(payload["ranking"], ranking)

    def test_broadcast_final_results_defaults_missing_score_to_zero(self):
        consumer = self.make_consumer()

        async_to_sync(consumer.broadcast_final_results)(
            {"ranking": [{"username": "anna", "score": 2}]}
        )

        payload = json.loads(consumer.send.await_args.kwargs["text_data"])
        self.assertEqual(payload["own_score"], 0)

    def test_broadcast_question_results_serializes_payload(self):
        consumer = self.make_consumer()
        event = {
            "correct_answer": 1,
            "results": [{"username": "john", "is_correct": True}],
        }

        async_to_sync(consumer.broadcast_question_results)(event)

        payload = json.loads(consumer.send.await_args.kwargs["text_data"])
        self.assertEqual(payload["type"], "question_results")
        self.assertEqual(payload["correct_answer"], 1)
        self.assertEqual(payload["results"], event["results"])

    def test_game_over_trigger_sends_event(self):
        consumer = self.make_consumer()

        async_to_sync(consumer.game_over_trigger)({})

        self.assertEqual(
            json.loads(consumer.send.await_args.kwargs["text_data"]),
            {"type": "game_over"},
        )

    @patch("games.consumers.GameService.get_score", new_callable=AsyncMock)
    @patch("games.consumers.GameService.get_users_in_room", new_callable=AsyncMock)
    def test_get_ranking_collects_scores(self, mock_users, mock_score):
        consumer = self.make_consumer()
        mock_users.return_value = ["john", "anna"]
        mock_score.side_effect = [2, 1]

        result = async_to_sync(consumer.get_ranking)()

        self.assertEqual(
            result,
            [
                {"username": "john", "score": 2},
                {"username": "anna", "score": 1},
            ],
        )
