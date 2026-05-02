from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from quiz.models import Quiz, Question

@api_view(["GET"])
def quizes_name_list(request):
    quiz_names = list(Quiz.objects.values_list("name", flat=True))
    return Response(quiz_names)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_quiz(request):
    """
    Create a new quiz instance along with its associated questions.

    Expected JSON structure:
    {
        "name": "Quiz Title",
        "questions": [
            {
                "text": "Question content?",
                "ans1": "Option A",
                "ans2": "Option B",
                "correct_ans": 0
            }
        ]
    }

    Args:
        request: The HTTP request object containing quiz and question data.

    Returns:
        Response: A success message with the created quiz ID or an error message.
    """
    quiz_name = request.data.get("name")
    questions = request.data.get("questions")

    if not quiz_name or not questions:
        return Response(
            {"error": "Both 'name' and 'questions' fields are required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    new_quiz = Quiz.objects.create(name=quiz_name)

    for q in questions:
        text = q.get("text")
        ans1 = q.get("ans1")
        ans2 = q.get("ans2")
        correct_ans = q.get("correct_ans", 0)

        Question.objects.create(
            text=text,
            ans1=ans1,
            ans2=ans2,
            correct_ans=correct_ans,
            quiz=new_quiz
        )

    return Response(
        {"status": "created", "quiz_id": new_quiz.id}, 
        status=status.HTTP_201_CREATED
    )