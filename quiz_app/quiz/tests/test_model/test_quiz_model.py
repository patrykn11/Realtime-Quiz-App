from django.test import TestCase
from quiz.models import Quiz, Question, Choice

class QuizModelTest(TestCase):

    def setUp(self):
        self.quiz = Quiz.objects.create(name="General Knowledge")

    def test_quiz_creation(self):
        self.assertEqual(self.quiz.name, "General Knowledge")
        self.assertIsNotNone(self.quiz.created_at)

    def test_quiz_str(self):
        self.assertEqual(str(self.quiz), "General Knowledge")

