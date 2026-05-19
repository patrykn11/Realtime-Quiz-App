from django.db import models


class Choice(models.Model):
    question = models.ForeignKey(
        "questions.Question",
        on_delete=models.CASCADE,
        related_name="choices",
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = "quiz_choice"

    def __str__(self):
        return self.text
