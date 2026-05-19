from django.db.models import Count
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import QuizHistory
from .serializers import (
    QuizHistoryRankingSerializer,
    QuizHistorySerializer,
    UserStatsPerDaySerializer,
)


class UserStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        histories = QuizHistory.objects.filter(user=request.user).order_by(
            "-quiz_time", "-id"
        )
        return Response(QuizHistorySerializer(histories, many=True).data)


class UserStatsPerDayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        histories = (
            QuizHistory.objects.filter(user=request.user)
            .values("quiz_time")
            .annotate(count=Count("id"))
            .order_by("quiz_time")
        )
        serializer = UserStatsPerDaySerializer(histories, many=True)
        return Response(serializer.data)


class QuizHistoryRankingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id):
        user_history = (
            QuizHistory.objects.select_related("quiz")
            .filter(game_id=game_id, user=request.user)
            .first()
        )
        if user_history is None:
            return Response(
                {"detail": "history not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        histories = (
            QuizHistory.objects.filter(game_id=game_id)
            .select_related("user")
            .order_by("-score", "user__username")
        )
        serializer = QuizHistoryRankingSerializer(
            user_history,
            context={"ranking": histories},
        )
        return Response(serializer.data)
