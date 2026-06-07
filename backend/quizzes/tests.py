from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from quizzes.models import Choice, Question, Quiz
from quizzes.serializers import (
    ChoiceCreateSerializer,
    QuestionCreateSerializer,
    QuizCreateSerializer,
)


User = get_user_model()


class QuizModelTest(TestCase):
    def setUp(self):
        self.quiz = Quiz.objects.create(name="General Knowledge")

    def test_quiz_creation(self):
        self.assertEqual(self.quiz.name, "General Knowledge")
        self.assertIsNotNone(self.quiz.created_at)

    def test_quiz_str(self):
        self.assertEqual(str(self.quiz), "General Knowledge")

    def test_name_cannot_exceed_32_characters(self):
        quiz = Quiz(name="x" * 33)

        with self.assertRaises(ValidationError):
            quiz.full_clean()

    def test_deleting_quiz_cascades_to_questions_and_choices(self):
        question = Question.objects.create(text="Question", quiz=self.quiz)
        choice = Choice.objects.create(question=question, text="Answer")

        self.quiz.delete()

        self.assertFalse(Question.objects.filter(id=question.id).exists())
        self.assertFalse(Choice.objects.filter(id=choice.id).exists())


class QuizApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test", email="test@example.com", password="pass"
        )
        self.client.force_authenticate(user=self.user)
        self.sample_quiz = Quiz.objects.create(name="sample_quiz")
        self.sample2_quiz = Quiz.objects.create(name="sample2_quiz")

    @staticmethod
    def valid_payload(name="sample3_quiz"):
        return {
            "name": name,
            "questions": [
                {
                    "text": "2+2?",
                    "choices": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True},
                    ],
                }
            ],
        }

    def test_quiz_list_api(self):
        response = self.client.get("/api/quizzes/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            [
                {"id": self.sample_quiz.id, "name": "sample_quiz"},
                {"id": self.sample2_quiz.id, "name": "sample2_quiz"},
            ],
        )

    def test_create_quiz_api(self):
        response = self.client.post(
            "/api/create_quiz/",
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"message": "Quiz created"})
        quiz = Quiz.objects.get(name="sample3_quiz")
        self.assertEqual(quiz.owner, self.user)
        question = Question.objects.get(quiz=quiz)
        self.assertEqual(question.choices.count(), 2)
        self.assertEqual(question.choices.get(is_correct=True).text, "4")

    def test_create_quiz_requires_authentication(self):
        client = APIClient()

        response = client.post(
            "/api/create_quiz/",
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Quiz.objects.filter(name="sample3_quiz").exists())

    def test_create_quiz_ignores_owner_from_request(self):
        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="pass",
        )
        payload = self.valid_payload(name="owned_quiz")
        payload["owner"] = other_user.id

        response = self.client.post("/api/create_quiz/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.get(name="owned_quiz").owner, self.user)

    def test_create_quiz_rejects_duplicate_name(self):
        response = self.client.post(
            "/api/create_quiz/",
            self.valid_payload(name="sample_quiz"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_create_quiz_rejects_empty_questions(self):
        response = self.client.post(
            "/api/create_quiz/",
            {"name": "empty", "questions": []},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("questions", response.data)
        self.assertFalse(Quiz.objects.filter(name="empty").exists())

    def test_create_quiz_rejects_invalid_choices(self):
        payload = self.valid_payload(name="invalid")
        payload["questions"][0]["choices"] = [
            {"text": "only answer", "is_correct": True}
        ]

        response = self.client.post("/api/create_quiz/", payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Quiz.objects.filter(name="invalid").exists())

    def test_owner_can_get_quiz_details(self):
        quiz = Quiz.objects.create(name="details", owner=self.user)
        question = Question.objects.create(text="2+2?", quiz=quiz)
        Choice.objects.create(question=question, text="3", is_correct=False)
        Choice.objects.create(question=question, text="4", is_correct=True)

        response = self.client.get(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], quiz.id)
        self.assertEqual(response.data["name"], "details")
        self.assertEqual(response.data["owner"], self.user.username)
        self.assertEqual(response.data["questions"][0]["text"], "2+2?")
        self.assertEqual(
            response.data["questions"][0]["choices"],
            [
                {"id": question.choices.all()[0].id, "text": "3", "is_correct": False},
                {"id": question.choices.all()[1].id, "text": "4", "is_correct": True},
            ],
        )

    def test_non_owner_cannot_get_quiz_details(self):
        owner = User.objects.create_user(
            username="details-owner",
            email="details-owner@example.com",
            password="pass",
        )
        quiz = Quiz.objects.create(name="private-details", owner=owner)

        response = self.client.get(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_quiz_details_requires_authentication(self):
        quiz = Quiz.objects.create(name="protected-details", owner=self.user)

        response = APIClient().get(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_delete_quiz_with_questions_and_choices(self):
        quiz = Quiz.objects.create(name="owned", owner=self.user)
        question = Question.objects.create(text="Question", quiz=quiz)
        choice = Choice.objects.create(question=question, text="Answer")

        response = self.client.delete(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Quiz.objects.filter(id=quiz.id).exists())
        self.assertFalse(Question.objects.filter(id=question.id).exists())
        self.assertFalse(Choice.objects.filter(id=choice.id).exists())

    def test_non_owner_cannot_delete_quiz(self):
        owner = User.objects.create_user(
            username="owner",
            email="owner@example.com",
            password="pass",
        )
        quiz = Quiz.objects.create(name="not-mine", owner=owner)

        response = self.client.delete(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Quiz.objects.filter(id=quiz.id).exists())

    def test_delete_quiz_requires_authentication(self):
        quiz = Quiz.objects.create(name="private", owner=self.user)

        response = APIClient().delete(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Quiz.objects.filter(id=quiz.id).exists())

    def test_delete_missing_quiz_returns_not_found(self):
        response = self.client.delete("/api/quizzes/999999/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MyQuizApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="quiz-owner",
            email="quiz-owner@example.com",
            password="pass",
        )
        self.other_user = User.objects.create_user(
            username="other-quiz-owner",
            email="other-quiz-owner@example.com",
            password="pass",
        )
        self.client.force_authenticate(user=self.user)

    def test_returns_only_authenticated_users_quizzes(self):
        first_quiz = Quiz.objects.create(name="First owned quiz", owner=self.user)
        second_quiz = Quiz.objects.create(name="Second owned quiz", owner=self.user)
        Question.objects.create(text="Question one", quiz=second_quiz)
        Question.objects.create(text="Question two", quiz=second_quiz)
        Quiz.objects.create(name="Someone else's quiz", owner=self.other_user)
        Quiz.objects.create(name="Quiz without owner")

        response = self.client.get("/api/my_quizzes/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            [quiz["id"] for quiz in response.data],
            [second_quiz.id, first_quiz.id],
        )
        self.assertEqual(
            [quiz["name"] for quiz in response.data],
            ["Second owned quiz", "First owned quiz"],
        )
        self.assertEqual(
            [quiz["question_count"] for quiz in response.data],
            [2, 0],
        )
        self.assertTrue(all("created_at" in quiz for quiz in response.data))

    def test_requires_authentication(self):
        response = APIClient().get("/api/my_quizzes/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class QuizSerializerTests(TestCase):
    @patch("quizzes.serializers.Choice.objects.bulk_create")
    def test_create_is_atomic_when_choice_creation_fails(self, mock_bulk_create):
        mock_bulk_create.side_effect = RuntimeError("database failure")
        serializer = QuizCreateSerializer(data=QuizApiTests.valid_payload("atomic"))
        self.assertTrue(serializer.is_valid(), serializer.errors)

        with self.assertRaises(RuntimeError):
            serializer.save()

        self.assertFalse(Quiz.objects.filter(name="atomic").exists())
        self.assertFalse(Question.objects.filter(text="2+2?").exists())


class QuestionModelTest(TestCase):
    def setUp(self):
        self.quiz = Quiz.objects.create(name="Science Quiz")
        self.question = Question.objects.create(text="testq", quiz=self.quiz)

    def test_question_fields(self):
        self.assertEqual(self.question.text, "testq")
        self.assertEqual(self.question.quiz, self.quiz)

    def test_question_relationship(self):
        self.assertEqual(self.quiz.questions.first(), self.question)

    def test_question_str(self):
        self.assertEqual(str(self.question), "testq")

    def test_created_at_is_set(self):
        self.assertIsNotNone(self.question.created_at)

    def test_deleting_quiz_deletes_question(self):
        question_id = self.question.id
        self.quiz.delete()
        self.assertFalse(Question.objects.filter(id=question_id).exists())


class QuestionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username="question-owner",
            email="question-owner@example.com",
            password="pass",
        )
        self.other_user = User.objects.create_user(
            username="question-other-user",
            email="question-other-user@example.com",
            password="pass",
        )
        self.quiz = Quiz.objects.create(name="Question API Quiz", owner=self.owner)
        self.question = Question.objects.create(
            text="Old question",
            quiz=self.quiz,
        )
        self.choice = Choice.objects.create(
            question=self.question,
            text="Answer",
            is_correct=True,
        )
        self.url = f"/api/question/{self.question.id}/"
        self.client.force_authenticate(user=self.owner)

    def test_owner_can_update_question(self):
        response = self.client.patch(
            self.url,
            {"text": "Updated question"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"text": "Updated question"})
        self.question.refresh_from_db()
        self.assertEqual(self.question.text, "Updated question")

    def test_update_question_rejects_empty_text(self):
        response = self.client.patch(self.url, {"text": ""}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.question.refresh_from_db()
        self.assertEqual(self.question.text, "Old question")

    def test_non_owner_cannot_update_question(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.patch(
            self.url,
            {"text": "Changed by another user"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.question.refresh_from_db()
        self.assertEqual(self.question.text, "Old question")

    def test_update_question_requires_authentication(self):
        response = APIClient().patch(
            self.url,
            {"text": "Anonymous change"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.question.refresh_from_db()
        self.assertEqual(self.question.text, "Old question")

    def test_owner_can_delete_question_and_its_choices(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Question.objects.filter(id=self.question.id).exists())
        self.assertFalse(Choice.objects.filter(id=self.choice.id).exists())

    def test_non_owner_cannot_delete_question(self):
        self.client.force_authenticate(user=self.other_user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Question.objects.filter(id=self.question.id).exists())

    def test_delete_question_requires_authentication(self):
        response = APIClient().delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Question.objects.filter(id=self.question.id).exists())

    def test_missing_question_returns_not_found(self):
        missing_url = "/api/question/999999/"

        patch_response = self.client.patch(
            missing_url,
            {"text": "Missing"},
            format="json",
        )
        delete_response = self.client.delete(missing_url)

        self.assertEqual(patch_response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(delete_response.status_code, status.HTTP_404_NOT_FOUND)


class QuestionSerializerTests(TestCase):
    def test_accepts_exactly_one_correct_choice(self):
        serializer = QuestionCreateSerializer(
            data={
                "text": "2+2?",
                "choices": [
                    {"text": "3", "is_correct": False},
                    {"text": "4", "is_correct": True},
                ],
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_rejects_fewer_than_two_choices(self):
        serializer = QuestionCreateSerializer(
            data={
                "text": "2+2?",
                "choices": [{"text": "4", "is_correct": True}],
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("at least two choices", str(serializer.errors))

    def test_rejects_question_without_correct_choice(self):
        serializer = QuestionCreateSerializer(
            data={
                "text": "2+2?",
                "choices": [
                    {"text": "3", "is_correct": False},
                    {"text": "4", "is_correct": False},
                ],
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("exactly one correct choice", str(serializer.errors))

    def test_rejects_multiple_correct_choices(self):
        serializer = QuestionCreateSerializer(
            data={
                "text": "2+2?",
                "choices": [
                    {"text": "3", "is_correct": True},
                    {"text": "4", "is_correct": True},
                ],
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("exactly one correct choice", str(serializer.errors))


class ChoiceModelTest(TestCase):
    def setUp(self):
        self.quiz = Quiz.objects.create(name="Math Quiz")
        self.question = Question.objects.create(text="2 + 2?", quiz=self.quiz)
        self.choice = Choice.objects.create(
            question=self.question,
            text="4",
            is_correct=True,
        )

    def test_choice_fields(self):
        self.assertEqual(self.choice.text, "4")
        self.assertTrue(self.choice.is_correct)
        self.assertEqual(self.choice.question, self.question)

    def test_choice_str(self):
        self.assertEqual(str(self.choice), "4")

    def test_incorrect_choice_str(self):
        choice = Choice.objects.create(
            question=self.question,
            text="5",
            is_correct=False,
        )
        self.assertEqual(str(choice), "5")

    def test_cascade_deletion(self):
        question_id = self.question.id
        self.question.delete()
        self.assertFalse(Choice.objects.filter(question_id=question_id).exists())

    def test_is_correct_defaults_to_false(self):
        choice = Choice.objects.create(question=self.question, text="5")
        self.assertFalse(choice.is_correct)

    def test_reverse_relation_contains_choices(self):
        self.assertEqual(list(self.question.choices.all()), [self.choice])


class ChoiceSerializerTests(TestCase):
    def test_serializes_choice_fields(self):
        quiz = Quiz.objects.create(name="Serializer Quiz")
        question = Question.objects.create(text="Question", quiz=quiz)
        choice = Choice.objects.create(
            question=question,
            text="Answer",
            is_correct=True,
        )
        data = ChoiceCreateSerializer(choice).data
        self.assertEqual(data, {"text": "Answer", "is_correct": True})

    def test_is_correct_is_optional_and_defaults_to_false(self):
        quiz = Quiz.objects.create(name="Default Quiz")
        question = Question.objects.create(text="Question", quiz=quiz)
        serializer = ChoiceCreateSerializer(data={"text": "Answer"})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        choice = serializer.save(question=question)
        self.assertFalse(choice.is_correct)
