from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Quiz, Question
from .serializers import (
    MyQuizListSerializer,
    QuizCreateSerializer,
    QuizDetailSerializer,
    QuizListSerializer,
    QuizUpdateSerializer,
    QuestionUpdateSerializer,
)
from .permission import IsQuizOwner


class QuestionDetailApiView(APIView):
    permission_classes = [IsAuthenticated, IsQuizOwner]

    def patch(self, request, question_id):
        question = get_object_or_404(
            Question,
            id=question_id
        )
        self.check_object_permissions(request, question.quiz)
        serializer = QuestionUpdateSerializer(
            question,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def delete(self, request, question_id):
        question = get_object_or_404(
            Question,
            id=question_id
        )

        self.check_object_permissions(request, question.quiz)

        question.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)




class QuizListAPIView(APIView):
    def get(self, request):
        quizzes = Quiz.objects.order_by("id")
        return Response(
            QuizListSerializer(quizzes, many=True).data,
            status=status.HTTP_200_OK,
        )


class MyQuizListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        quizzes = (
            Quiz.objects.filter(owner=request.user)
            .annotate(question_count=Count("questions"))
            .order_by("-created_at", "-id")
        )
        return Response(
            MyQuizListSerializer(quizzes, many=True).data,
            status=status.HTTP_200_OK,
        )


class CreateQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response({"message": "Quiz created"}, status=status.HTTP_201_CREATED)


class QuizDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsQuizOwner]

    def get_quiz(self, request, quiz_id):
        quiz = get_object_or_404(
            Quiz.objects.select_related("owner").prefetch_related(
                "questions__choices"
            ),
            id=quiz_id
        )
        self.check_object_permissions(request, quiz)
        return quiz

    def get(self, request, quiz_id):
        quiz = self.get_quiz(request, quiz_id)
        return Response(
            QuizDetailSerializer(quiz).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, quiz_id):
        quiz = self.get_quiz(request, quiz_id)
        serializer = QuizUpdateSerializer(
            quiz,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, quiz_id):
        quiz = self.get_quiz(request, quiz_id)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
