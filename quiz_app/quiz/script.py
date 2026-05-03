import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from quiz.models import Quiz, Question, Choice

def seed_data():
    quiz, created = Quiz.objects.get_or_create(name="General Knowledge2")
    
    data = [
        {
            "text": "What color is the sky on a clear day?",
            "choices": [
                {"text": "Blue", "is_correct": True},
                {"text": "Green", "is_correct": False},
                {"text": "Red", "is_correct": False},
            ]
        },
        {
            "text": "Which planet is known as the Red Planet?",
            "choices": [
                {"text": "Mars", "is_correct": True},
                {"text": "Venus", "is_correct": False},
                {"text": "Jupiter", "is_correct": False},
                {"text": "Saturn", "is_correct": False},
            ]
        }
    ]

    for item in data:
        question, q_created = Question.objects.get_or_create(text=item["text"], quiz=quiz)
        for c_data in item["choices"]:
            Choice.objects.create(
            question=question,
            text=c_data["text"],
            is_correct=c_data["is_correct"]
            )


if __name__ == "__main__":
    seed_data()