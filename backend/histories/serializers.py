from rest_framework import serializers

from .models import QuizHistory


class QuizHistorySerializer(serializers.ModelSerializer):
    quiz_name = serializers.CharField(source="quiz.name")
    created_at = serializers.DateField(source="quiz_time")

    class Meta:
        model = QuizHistory
        fields = ("id", "game_id", "quiz_name", "score", "created_at")


class UserStatsPerDaySerializer(serializers.Serializer):
    date = serializers.DateField(source="quiz_time")
    quizzes_played = serializers.IntegerField(source="count")


class QuizHistoryRankingEntrySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    score = serializers.SerializerMethodField()

    class Meta:
        model = QuizHistory
        fields = ("username", "score")

    def get_score(self, obj):
        return obj.score or 0


class QuizHistoryRankingSerializer(serializers.ModelSerializer):
    quiz_name = serializers.CharField(source="quiz.name")
    date = serializers.DateField(source="quiz_time")
    own_score = serializers.SerializerMethodField()
    ranking = serializers.SerializerMethodField()

    class Meta:
        model = QuizHistory
        fields = ("game_id", "quiz_name", "date", "own_score", "ranking")

    def get_own_score(self, obj):
        return obj.score or 0

    def get_ranking(self, obj):
        histories = self.context["ranking"]
        return QuizHistoryRankingEntrySerializer(histories, many=True).data
