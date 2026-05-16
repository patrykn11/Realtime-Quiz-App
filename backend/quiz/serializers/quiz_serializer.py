from django.db import transaction
from rest_framework import serializers

from quiz.models import Choice, Question, Quiz
from .question_serializer import QuestionCreateSerializer


class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuestionCreateSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ("name", "questions")

    def validate_name(self, value):
        if Quiz.objects.filter(name=value).exists():
            raise serializers.ValidationError("quiz with this name already exists")
        return value

    def validate_questions(self, value):
        if not value:
            raise serializers.ValidationError("quiz must have at least one question")
        return value

    def create(self, validated_data):
        questions_data = validated_data.pop("questions")

        with transaction.atomic():
            quiz = Quiz.objects.create(**validated_data)

            for question_data in questions_data:
                choices_data = question_data.pop("choices")
                question = Question.objects.create(quiz=quiz, **question_data)
                Choice.objects.bulk_create([
                    Choice(question=question, **choice_data)
                    for choice_data in choices_data
                ])

        return quiz
