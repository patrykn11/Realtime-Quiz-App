from django.test import TestCase

from questions.serializers import QuestionCreateSerializer
from questions.models import Question
from quizzes.models import Quiz


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
