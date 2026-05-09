
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from quiz.models import QuizHistory
from quiz.serializers import QuizHistorySerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_stats(request):
    all_user_quizes = QuizHistory.objects.filter(user=request.user).order_by("-quiz_time", "-id")
    serializer = QuizHistorySerializer(all_user_quizes, many=True)
    return Response(serializer.data)
    

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_stats_per_day(request):
    
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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def quiz_history_ranking(request, history_id):
    try:
        history = QuizHistory.objects.select_related("quiz").get(
            id=history_id,
            user=request.user
        )
    except QuizHistory.DoesNotExist:
        return Response({"detail": "history not found"}, status=status.HTTP_404_NOT_FOUND)

    histories = (
        QuizHistory.objects
        .filter(quiz=history.quiz, quiz_time=history.quiz_time)
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
        "quiz_name": history.quiz.name,
        "date": str(history.quiz_time),
        "own_score": history.score or 0,
        "ranking": ranking
    })
