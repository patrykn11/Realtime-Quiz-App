from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from quiz.models import Quiz, Question

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_quiz(request):
    """
    Create a quiz with multiple questions, each having two answers and a correct answer index.
    """
    
    quiz_name = request.data.get("name")
    questions = request.data.get("questions")

    if not quiz_name or not questions:
        return Response({"error": "Name and questions required"}, status=400)

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

    return Response({"status": "created", "quiz_id": new_quiz.id})