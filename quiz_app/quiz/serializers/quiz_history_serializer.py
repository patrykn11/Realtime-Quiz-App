from rest_framework import serializers

from quiz.models import QuizHistory


class QuizHistorySerializer(serializers.ModelSerializer):
    quiz_name = serializers.CharField(source="quiz.name")
    created_at = serializers.DateField(source="quiz_time")

    class Meta:
        model = QuizHistory
        fields = ("quiz_name", "score", "created_at")
