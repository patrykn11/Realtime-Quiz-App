from django.urls import path

from .views import (
    CreateQuizAPIView,
    MyQuizListAPIView,
    QuizDetailAPIView,
    QuizListAPIView,
    QuestionDetailApiView,
)


app_name = "quizzes"
urlpatterns = [
    path("quizzes/", QuizListAPIView.as_view(), name="list"),
    path("my_quizzes/", MyQuizListAPIView.as_view(), name="my-list"),
    path("create_quiz/", CreateQuizAPIView.as_view(), name="create"),
    path("quizzes/<int:quiz_id>/", QuizDetailAPIView.as_view(), name="detail"),
    path(
        "question/<int:question_id>/",
        QuestionDetailApiView.as_view(),
        name="question-detail",
    ),
]
