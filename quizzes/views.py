
from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from quizzes.functions import generate_quiz_data
from quizzes.models import Question, Quiz



class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url = request.data.get("url")

        if not url:
            return Response(
                {"error": "A YouTube URL is required."},
                status=400,
            )

        try:
            URLValidator()(url)
        except ValidationError:
            return Response(
                {"error": "A valid URL is required."},
                status=400,
            )

        if not self.is_youtube_url(url):
            return Response(
                {"error": "A YouTube URL is required."},
                status=400,
            )

        quiz_data = generate_quiz_data(url)
        quiz = Quiz.objects.create(
            user=request.user,
            title=quiz_data["title"],
            description=quiz_data["description"],
            video_url=url,
        )

        Question.objects.bulk_create(
            [
                Question(
                    quiz=quiz,
                    question_title=question["question_title"],
                    question_options=question["question_options"],
                    answer=question["answer"],
                )
                for question in quiz_data["questions"]
            ]
        )

        return Response(
            {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "video_url": quiz.video_url,
                "questions": quiz_data["questions"],
            },
            status=201,
        )

    def is_youtube_url(self, url):
        hostname = urlparse(url).hostname or ""
        allowed_domains = {
            "youtube.com",
            "www.youtube.com",
            "youtu.be",
        }

        return hostname.lower() in allowed_domains
