from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from quiz.models import Quiz
from quiz.serializers import QuizCreateSerializer


class QuizesNameListAPIView(APIView):
    def get(self, request):
        quiz_names = list(Quiz.objects.values_list("name", flat=True))
        return Response(quiz_names)


class CreateQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Quiz created"}, status=status.HTTP_201_CREATED)
