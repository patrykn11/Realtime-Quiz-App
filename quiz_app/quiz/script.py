import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from quiz.models import Quiz, Question

quiz, created = Quiz.objects.get_or_create(name="sample")

questions_data = [
    {"text": "Jakie jest stolica Polski?", "ans1": "Warszawa", "ans2": "Kraków", "correct_ans": 0},
    {"text": "2 + 2 = ?", "ans1": "3", "ans2": "4", "correct_ans": 1},
    {"text": "Jaki kolor ma niebo?", "ans1": "Niebieski", "ans2": "Zielony", "correct_ans": 0},
]

for qdata in questions_data:
    Question.objects.get_or_create(quiz=quiz, text=qdata["text"], defaults={
        "ans1": qdata["ans1"],
        "ans2": qdata["ans2"],
        "correct_ans": qdata["correct_ans"]
    })

print("Initial quiz and questions created successfully.")