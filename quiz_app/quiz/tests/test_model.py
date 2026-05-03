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

class QuestionModelTest(TestCase):

    def setUp(self):
        self.quiz = Quiz.objects.create(name="Science Quiz")
        self.question = Question.objects.create(
            text="testq",
            quiz=self.quiz
        )

    def test_question_fields(self):
        self.assertEqual(self.question.text, "testq")
        self.assertEqual(self.question.quiz, self.quiz)

    def test_question_relationship(self):
        self.assertEqual(self.quiz.questions.count(), 1)
        self.assertEqual(self.quiz.questions.first(), self.question)

    def test_question_str(self):
        self.assertEqual(str(self.question), "testq")

class ChoiceModelTest(TestCase):

    def setUp(self):
        self.quiz = Quiz.objects.create(name="Math Quiz")
        self.question = Question.objects.create(text="2 + 2?", quiz=self.quiz)
        self.choice = Choice.objects.create(
            question=self.question,
            text="4",
            is_correct=True
        )

    def test_choice_fields(self):
        self.assertEqual(self.choice.text, "4")
        self.assertTrue(self.choice.is_correct)
        self.assertEqual(self.choice.question, self.question)

    def test_choice_str(self):
        self.assertEqual(str(self.choice), "4")

    def test_choice_incorrect_str(self):
        incorrect_choice = Choice.objects.create(
            question=self.question,
            text="5",
            is_correct=False
        )
        self.assertEqual(str(incorrect_choice), "5")

    def test_cascade_deletion(self):
        question_id = self.question.id
        self.question.delete()
        self.assertFalse(Choice.objects.filter(question_id=question_id).exists())