
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from django.db.models.functions import TruncDate
from quiz.models import QuizHistory


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_stats(request):
    all_user_quizes = QuizHistory.objects.filter(user=request.user)
    data = []
    for quiz_history in all_user_quizes:

        data.append({

            "quiz_name": quiz_history.quiz.name,

            "score": quiz_history.score,

            "created_at": quiz_history.quiz_time

        })
        print(quiz_history.quiz.name)
    return Response(data)
    

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

