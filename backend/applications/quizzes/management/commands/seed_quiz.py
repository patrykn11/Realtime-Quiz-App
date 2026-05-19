from django.core.management.base import BaseCommand

from applications.choices.models import Choice
from applications.questions.models import Question
from applications.quizzes.models import Quiz


class Command(BaseCommand):
    help = "Create the sample general-knowledge quiz"

    def handle(self, *args, **options):
        quiz, _ = Quiz.objects.get_or_create(name="General Knowledge2")
        data = [
            {
                "text": "What color is the sky?",
                "choices": [
                    {"text": "Blue", "is_correct": True},
                    {"text": "Green", "is_correct": False},
                    {"text": "Red", "is_correct": False},
                ],
            },
            {
                "text": "Which planet is known as the Red Planet?",
                "choices": [
                    {"text": "Mars", "is_correct": True},
                    {"text": "Venus", "is_correct": False},
                    {"text": "Jupiter", "is_correct": False},
                    {"text": "Saturn", "is_correct": False},
                ],
            },
        ]

        for item in data:
            question, created = Question.objects.get_or_create(
                text=item["text"], quiz=quiz
            )
            if created:
                Choice.objects.bulk_create(
                    [Choice(question=question, **choice) for choice in item["choices"]]
                )

        self.stdout.write(self.style.SUCCESS("Sample quiz is ready."))
