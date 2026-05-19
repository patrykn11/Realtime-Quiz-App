from django.db import models


class Question(models.Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    quiz = models.ForeignKey(
        "quizzes.Quiz",
        on_delete=models.CASCADE,
        related_name="questions",
    )

    class Meta:
        db_table = "quiz_question"

    def __str__(self):
        return self.text
