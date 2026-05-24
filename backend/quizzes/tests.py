from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from choices.models import Choice
from questions.models import Question
from quizzes.models import Quiz
from quizzes.serializers import QuizCreateSerializer


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
        self.user = User.objects.create_user(username="test", password="pass")
        self.client.force_authenticate(user=self.user)
        Quiz.objects.create(name="sample_quiz")
        Quiz.objects.create(name="sample2_quiz")

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

    def test_quiz_name_list_api(self):
        response = self.client.get("/api/quizes_name/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, ["sample_quiz", "sample2_quiz"])

    def test_create_quiz_api(self):
        response = self.client.post(
            "/api/create_quiz/",
            self.valid_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"message": "Quiz created"})
        quiz = Quiz.objects.get(name="sample3_quiz")
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
