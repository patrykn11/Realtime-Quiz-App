from django.test import TestCase
from quiz.models import Quiz, Question
from django.contrib.auth.models import User
from rest_framework.test import APIClient


class QuizApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="test", password="pass")
        self.client.force_authenticate(user=self.user)

        Quiz.objects.create(name="sample_quiz")
        Quiz.objects.create(name="sample2_quiz")

    def test_quiz_name_list_api(self):
        response = self.client.get("/api/quizes_name/")
        data = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, ["sample_quiz", "sample2_quiz"])

    def test_create_quiz_api(self):
        payload = {
            "name": "sample3_quiz",
            "questions": [
                {
                    "text": "2+2?",
                    "choices": [
                        {"text": "3", "is_correct": False},
                        {"text": "4", "is_correct": True}
                    ]
                },
                {
                    "text": "2+3?",
                    "choices": [
                        {"text": "4", "is_correct": False},
                        {"text": "5", "is_correct": True}
                    ]
                }
            ]
        }

        response = self.client.post("/api/create_quiz/", payload, format="json")
        self.assertEqual(response.status_code, 201)

        quiz = Quiz.objects.get(name="sample3_quiz")
        self.assertIsNotNone(quiz)

        questions = Question.objects.filter(quiz=quiz)
        self.assertEqual(questions.count(), 2)

        question1 = questions.get(text="2+2?")
        self.assertEqual(question1.choices.count(), 2)
        self.assertTrue(question1.choices.filter(text="4", is_correct=True).exists())
        self.assertTrue(question1.choices.filter(text="3", is_correct=False).exists())