
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from quiz.models import Quiz, Question
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_quiz(request):
    quiz_name = request.data.get("name")
    questions = request.data.get("questions")
    correct_answer = request.data.get("answer")
    if not quiz_name or not questions:
        return Response({"error": "Name and questions required"}, status=400)

    new_quiz = Quiz.objects.create(quiz=quiz_name)
    for question in questions:
        Question.objects.create(text=question, quiz=new_quiz)

    return Response({
        "status": "created"
    })