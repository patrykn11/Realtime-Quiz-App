from django.db import models
from .Quiz import Quiz
class Question(models.Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    ans1 = models.CharField(max_length=256)
    ans2 = models.CharField(max_length=256)
    correct_ans = models.IntegerField(null=False)

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="question"
        )
    
    answer = models.IntegerField(null=False)    

    def __str__(self):
        return self.text

