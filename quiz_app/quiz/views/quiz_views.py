from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from quiz.models import Quiz, Question, Choice

@api_view(["GET"])
def quizes_name_list(request):
    quiz_names = list(Quiz.objects.values_list("name", flat=True))
    return Response(quiz_names)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_quiz(request):
    data = request.data
    quiz = Quiz.objects.create(name=data.get('name'))
    questions_data = data.get('questions', [])

    for q_item in questions_data:
        question = Question.objects.create(
            quiz=quiz,
            text=q_item.get('text')
        )
        
        choices_data = q_item.get('choices', [])
        for c_item in choices_data:
            Choice.objects.create(
                question=question,
                text=c_item.get('text'),
                is_correct=c_item.get('is_correct', False)
            )

    return Response({"message": "Quiz created"}, status=status.HTTP_201_CREATED)