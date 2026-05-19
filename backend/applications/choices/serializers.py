from rest_framework import serializers

from .models import Choice


class ChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("text", "is_correct")
