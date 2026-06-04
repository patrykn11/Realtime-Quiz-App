from django.db import transaction
from rest_framework import serializers

from .models import Choice, Question, Quiz


class QuizListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ("id", "name")


class MyQuizListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = ("id", "name", "created_at", "question_count")


class ChoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("text", "is_correct")


class ChoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ("id", "text", "is_correct")


class QuestionCreateSerializer(serializers.ModelSerializer):
    choices = ChoiceCreateSerializer(many=True)

    class Meta:
        model = Question
        fields = ("text", "choices")

    def validate_choices(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("question must have at least two choices")

        correct_choices = [choice for choice in value if choice.get("is_correct")]
        if len(correct_choices) != 1:
            raise serializers.ValidationError(
                "question must have exactly one correct choice"
            )

        return value


class QuestionDetailSerializer(serializers.ModelSerializer):
    choices = ChoiceDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ("id", "text", "created_at", "choices")


class QuizCreateSerializer(serializers.ModelSerializer):
    questions = QuestionCreateSerializer(many=True)

    class Meta:
        model = Quiz
        fields = ("name", "owner", "questions")
        read_only_fields = ("owner",)

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
                Choice.objects.bulk_create(
                    [
                        Choice(question=question, **choice_data)
                        for choice_data in choices_data
                    ]
                )

        return quiz


class QuizUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ("name",)

    def validate_name(self, value):
        duplicate_exists = (
            Quiz.objects.filter(name=value)
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if duplicate_exists:
            raise serializers.ValidationError("quiz with this name exists")

        return value


class QuizDetailSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(
        source="owner.username",
        read_only=True,
        allow_null=True,
    )
    questions = QuestionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ("id", "name", "owner", "created_at", "questions")


class QuestionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("text",)
