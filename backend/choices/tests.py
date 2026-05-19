from django.test import TestCase

from choices.models import Choice
from questions.models import Question
from quizzes.models import Quiz


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
