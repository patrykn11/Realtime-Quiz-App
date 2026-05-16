from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from quiz.models import Quiz
from quiz.serializers import QuizCreateSerializer

@api_view(["GET"])
def quizes_name_list(request):
    quiz_names = list(Quiz.objects.values_list("name", flat=True))
    return Response(quiz_names)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz(request):
    serializer = QuizCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response({"message": "Quiz created"}, status=status.HTTP_201_CREATED)
