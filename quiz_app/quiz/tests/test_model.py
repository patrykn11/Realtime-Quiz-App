from django.test import TestCase
from quiz.models import Quiz, Question

class ModelTest(TestCase):

    def setUp(self):
        self.quiz = Quiz.objects.create(
            name="Quiz 1",
        )

        self.question = Question.objects.create(
            text="Who was first president of USA?",
            ans1="Washington",
            ans2="Lincoln",
            correct_ans=1,
            quiz=self.quiz
        )

    def test_question_created(self):
        self.assertEqual(self.question.text, "Who was first president of USA?")
        self.assertEqual(self.question.quiz, self.quiz)

    def test_quiz_has_question(self):
        questions = self.quiz.question.all()
        self.assertEqual(questions.count(), 1)
        self.assertEqual(questions.first().text, self.question.text)