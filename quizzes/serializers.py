
"""Define serializers for quiz creation, retrieval, and updates."""

from urllib.parse import urlparse

from django.db import transaction
from rest_framework import serializers

from quizzes.models import Question, Quiz


def validate_youtube_url(value):
    """Ensure that a URL belongs to an allowed YouTube domain."""
    hostname = (urlparse(value).hostname or "").lower()
    allowed_domains = {
        "youtube.com",
        "www.youtube.com",
        "youtu.be",
    }

    if hostname not in allowed_domains:
        raise serializers.ValidationError(
            "A YouTube URL is required."
        )

    return value


class CreateQuizSerializer(serializers.Serializer):
    """Validate the URL submitted for quiz generation."""

    url = serializers.URLField()

    def validate_url(self, value):
        """Validate the submitted YouTube URL."""
        return validate_youtube_url(value)


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize and validate individual quiz questions."""

    def validate_question_options(self, value):
        """Require exactly four unique, non-empty answer options."""
        if not isinstance(value, list) or len(value) != 4:
            raise serializers.ValidationError(
                "Exactly four answer options are required."
            )

        if not all(
            isinstance(option, str) and option.strip()
            for option in value
        ):
            raise serializers.ValidationError(
                "All answer options must be non-empty strings."
            )

        if len({option.strip() for option in value}) != 4:
            raise serializers.ValidationError(
                "Answer options must be unique."
            )

        return value

    def validate(self, data):
        """Ensure that the correct answer is one of the options."""
        options = data.get(
            "question_options",
            getattr(self.instance, "question_options", []),
        )
        answer = data.get(
            "answer",
            getattr(self.instance, "answer", None),
        )

        if answer is not None and answer not in options:
            raise serializers.ValidationError(
                "The answer must be one of the question options."
            )

        return data

    class Meta:
        model = Question
        fields = [
            "id",
            "question_title",
            "question_options",
            "answer",
            "created_at",
            "updated_at",
        ]


class CreateQuizDataSerializer(serializers.ModelSerializer):
    """Create a quiz together with its associated questions."""

    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = [
            "title",
            "description",
            "video_url",
            "questions",
        ]

    @transaction.atomic
    def create(self, validated_data):
        """Create a quiz and all its questions atomically."""
        questions_data = validated_data.pop("questions")
        user = validated_data.pop("user")

        quiz = Quiz.objects.create(user=user, **validated_data)

        Question.objects.bulk_create(
            [
                Question(quiz=quiz, **question_data)
                for question_data in questions_data
            ]
        )

        return quiz


class QuizSerializer(serializers.ModelSerializer):
    """Serialize a quiz including its questions."""

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "updated_at",
            "video_url",
            "questions",
        ]


class UpdateQuizSerializer(serializers.ModelSerializer):
    """Validate and update existing quiz information."""

    def validate_video_url(self, value):
        """Validate the updated YouTube URL."""
        return validate_youtube_url(value)

    class Meta:
        model = Quiz
        fields = [
            "title",
            "description",
            "video_url",
        ]
