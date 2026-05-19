from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from applications.questions.models import Question
from applications.quizzes.models import Quiz


class QuizModelTest(TestCase):
    def setUp(self):
        self.quiz = Quiz.objects.create(name="General Knowledge")

    def test_quiz_creation(self):
        self.assertEqual(self.quiz.name, "General Knowledge")
        self.assertIsNotNone(self.quiz.created_at)

    def test_quiz_str(self):
        self.assertEqual(str(self.quiz), "General Knowledge")


class QuizApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test", password="pass")
        self.client.force_authenticate(user=self.user)
        Quiz.objects.create(name="sample_quiz")
        Quiz.objects.create(name="sample2_quiz")

    def test_quiz_name_list_api(self):
        response = self.client.get("/api/quizes_name/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, ["sample_quiz", "sample2_quiz"])

    def test_create_quiz_api(self):
        payload = {
            "name": "sample3_quiz",
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

        response = self.client.post("/api/create_quiz/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        quiz = Quiz.objects.get(name="sample3_quiz")
        self.assertEqual(Question.objects.filter(quiz=quiz).count(), 1)
