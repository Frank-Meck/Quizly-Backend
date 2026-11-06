
"""Handle API requests for creating and managing quizzes."""

from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from quizzes.functions import generate_quiz_data
from quizzes.models import Quiz
from quizzes.serializers import (
    CreateQuizDataSerializer,
    CreateQuizSerializer,
    QuizSerializer,
    UpdateQuizSerializer,
)


class CreateQuizView(APIView):
    """Handle quiz creation and retrieval of the user's quizzes."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Generate and save a quiz from a YouTube URL."""
        input_serializer = CreateQuizSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        url = input_serializer.validated_data["url"]

        quiz_data = generate_quiz_data(url)
        quiz_data["video_url"] = url

        serializer = CreateQuizDataSerializer(data=quiz_data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save(user=request.user)

        return Response(
            QuizSerializer(quiz).data,
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        """Return all quizzes belonging to the authenticated user."""
        quizzes = Quiz.objects.filter(user=request.user)
        serializer = QuizSerializer(quizzes, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class GetQuizView(APIView):
    """Handle retrieval, updating, and deletion of individual quizzes."""

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Return a quiz belonging to the authenticated user."""
        quiz = get_object_or_404(
            Quiz,
            pk=pk,
            user=request.user,
        )
        serializer = QuizSerializer(quiz)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        """Update a quiz belonging to the authenticated user."""
        quiz = get_object_or_404(
            Quiz,
            pk=pk,
            user=request.user,
        )
        serializer = UpdateQuizSerializer(
            quiz,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            QuizSerializer(quiz).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        """Delete a quiz belonging to the authenticated user."""
        quiz = get_object_or_404(
            Quiz,
            pk=pk,
            user=request.user,
        )
        quiz.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
