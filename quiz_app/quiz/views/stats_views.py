
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count
from quiz.models import QuizHistory
from quiz.serializers import QuizHistorySerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_stats(request):
    all_user_quizes = QuizHistory.objects.filter(user=request.user)
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
