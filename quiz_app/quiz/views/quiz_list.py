from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from quiz.models import Quiz

@api_view(["GET"])
def quizes_name_list(request):
    quiz_names = list(Quiz.objects.values_list("name", flat=True))
    return Response(quiz_names)
