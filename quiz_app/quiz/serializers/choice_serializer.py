from rest_framework import serializers

from quiz.models import Choice


class ChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("text", "is_correct")
