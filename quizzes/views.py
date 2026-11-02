from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from quizzes.functions import generate_quiz_data
from quizzes.models import Quiz
from quizzes.serializers import (
    CreateQuizDataSerializer,
    CreateQuizSerializer,
    QuizSerializer,
)


class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_serializer = CreateQuizSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        url = input_serializer.validated_data["url"]

        quiz_data = generate_quiz_data(url)
        quiz_data["video_url"] = url

        serializer = CreateQuizDataSerializer(data=quiz_data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save(
            user=request.user,
        )

        return Response(QuizSerializer(quiz).data, status=201)


class GetQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        quiz = get_object_or_404(
            Quiz,
            pk=pk,
            user=request.user,
        )
        serializer = QuizSerializer(quiz)

        return Response(serializer.data, status=200)