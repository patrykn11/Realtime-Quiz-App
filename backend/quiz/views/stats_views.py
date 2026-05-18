
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Count
from quiz.models import QuizHistory
from quiz.serializers import QuizHistorySerializer


class UserStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_user_quizes = QuizHistory.objects.filter(
            user=request.user
        ).order_by("-quiz_time", "-id")
        serializer = QuizHistorySerializer(all_user_quizes, many=True)
        return Response(serializer.data)


class UserStatsPerDayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            QuizHistory.objects
            .filter(user=request.user)
            .values("quiz_time")
            .annotate(count=Count("id"))
            .order_by("quiz_time")
        )

        data = [
            {
                "date": str(item["quiz_time"]),
                "quizzes_played": item["count"]
            }
            for item in qs
        ]

        return Response(data)


class QuizHistoryRankingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, game_id):
        user_history = (
            QuizHistory.objects
            .select_related("quiz")
            .filter(game_id=game_id, user=request.user)
            .first()
        )

        if user_history is None:
            return Response(
                {"detail": "history not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        histories = (
            QuizHistory.objects
            .filter(game_id=game_id)
            .select_related("user")
            .order_by("-score", "user__username")
        )

        ranking = [
            {
                "username": item.user.username,
                "score": item.score or 0
            }
            for item in histories
        ]

        return Response({
            "game_id": str(game_id),
            "quiz_name": user_history.quiz.name,
            "date": str(user_history.quiz_time),
            "own_score": user_history.score or 0,
            "ranking": ranking
        })
