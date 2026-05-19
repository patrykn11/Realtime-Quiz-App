from django.test import TestCase

from applications.questions.models import Question
from applications.quizzes.models import Quiz


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
