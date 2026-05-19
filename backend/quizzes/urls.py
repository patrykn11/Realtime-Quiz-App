from django.urls import path

from .views import CreateQuizAPIView, QuizzesNameListAPIView


app_name = "quizzes"
urlpatterns = [
    path("quizes_name/", QuizzesNameListAPIView.as_view(), name="names"),
    path("create_quiz/", CreateQuizAPIView.as_view(), name="create"),
]
