
from urllib.parse import urlparse

from rest_framework import serializers

from quizzes.models import Question, Quiz


class CreateQuizSerializer(serializers.Serializer):
    url = serializers.URLField()

    def validate_url(self, value):
        hostname = urlparse(value).hostname or ""
        allowed_domains = {
            "youtube.com",
            "www.youtube.com",
            "youtu.be",
        }

        if hostname.lower() not in allowed_domains:
            raise serializers.ValidationError(
                "A YouTube URL is required."
            )

        return value



class QuestionSerializer(serializers.ModelSerializer):

    def validate_question_options(self, value):
        if not isinstance(value, list) or len(value) != 4:
            raise serializers.ValidationError(
                "Exactly four answer options are required."
            )

        return value

    def validate(self, data):
        options = data.get("question_options", [])
        answer = data.get("answer")

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
        ]


class CreateQuizDataSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Quiz
        fields = [
            "title",
            "description",
            "video_url",
            "questions",
        ]

    def create(self, validated_data):
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
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "video_url",
            "questions",
        ]


class UpdateQuizSerializer(serializers.ModelSerializer):

    def validate_video_url(self, value):
        hostname = urlparse(value).hostname or ""
        allowed_domains = {
            "youtube.com",
            "www.youtube.com",
            "youtu.be",
        }

        if hostname.lower() not in allowed_domains:
            raise serializers.ValidationError(
                "A YouTube URL is required."
            )

        return value

    class Meta:
        model = Quiz
        fields = [
            "title",
            "description",
            "video_url",
        ]
