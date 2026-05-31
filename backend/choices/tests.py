from django.test import TestCase

from choices.models import Choice
from choices.serializers import ChoiceCreateSerializer
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
