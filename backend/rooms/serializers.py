from rest_framework import serializers

from quizzes.models import Quiz


class RoomCreateSerializer(serializers.Serializer):
    quiz_id = serializers.PrimaryKeyRelatedField(
        queryset=Quiz.objects.all(),
        source="quiz",
    )
