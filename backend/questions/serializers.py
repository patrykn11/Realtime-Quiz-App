from rest_framework import serializers

from choices.serializers import ChoiceCreateSerializer
from .models import Question


class QuestionCreateSerializer(serializers.ModelSerializer):
    choices = ChoiceCreateSerializer(many=True)

    class Meta:
        model = Question
        fields = ("text", "choices")

    def validate_choices(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("question must have at least two choices")

        correct_choices = [choice for choice in value if choice.get("is_correct")]
        if len(correct_choices) != 1:
            raise serializers.ValidationError(
                "question must have exactly one correct choice"
            )

        return value
