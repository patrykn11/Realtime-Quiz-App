from django.db import models
from django.conf import settings 
import uuid
from .Quiz import Quiz

class QuizHistory(models.Model):
    game_id = models.UUIDField(default=uuid.uuid4, db_index=True)

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

    quiz_time = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.quiz} - {self.score}"
