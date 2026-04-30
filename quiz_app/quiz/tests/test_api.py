from django.test import TestCase
from quiz.models import Quiz, Question
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class ApiQuiz(TestCase):
    
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
                    "ans1": "3",
                    "ans2": "4",
                    "correct_ans": 2 },
                {
                    "text": "2+3?",
                    "ans1": "4",
                    "ans2": "5",
                    "correct_ans": 2}]}
        


        
        response = self.client.post("/api/create_quiz/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        quiz = Quiz.objects.get(name="sample3_quiz")
        self.assertIsNotNone(quiz)
        questions = Question.objects.filter(quiz=quiz)
        self.assertEqual(questions.count(), 2)
        question1 = questions.get(text="2+2?")
        self.assertEqual(question1.ans1, "3")
        self.assertEqual(question1.ans2, "4")
        self.assertEqual(question1.correct_ans, 2)

    

