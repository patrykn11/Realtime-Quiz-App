from django.db import models
from django.conf import settings 
from .Quiz import Quiz

class QuizHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_histories_user"
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="quiz_histories_quiz"
    )

    score = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.user} - {self.quiz} - {self.score}"