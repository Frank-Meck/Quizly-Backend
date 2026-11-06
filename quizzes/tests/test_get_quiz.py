
"""Test quiz serialization and retrieval through the API."""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from quizzes.models import Question, Quiz
from quizzes.serializers import QuizSerializer


User = get_user_model()


class GetQuizSerializerTests(APITestCase):
    """Test serialization of quizzes and their associated questions."""

    def test_quiz_serializer_includes_questions(self):
        """Include associated questions in the serialized quiz."""
        user = User.objects.create_user(
            username="quiz_user",
            password="StrongPass123!",
        )
        quiz = Quiz.objects.create(
            user=user,
            title="Python Basics",
            description="An introduction to Python.",
            video_url="https://www.youtube.com/watch?v=example",
        )
        Question.objects.create(
            quiz=quiz,
            question_title="What is Python?",
            question_options=[
                "Language",
                "Browser",
                "Database",
                "Editor",
            ],
            answer="Language",
        )

        data = QuizSerializer(quiz).data

        self.assertEqual(data["title"], "Python Basics")
        self.assertEqual(len(data["questions"]), 1)
        self.assertEqual(
            data["questions"][0]["question_title"],
            "What is Python?",
        )


class GetQuizTests(APITestCase):
    """Test retrieving individual quizzes through the API."""

    def test_user_can_retrieve_own_quiz(self):
        """Allow users to retrieve their own quizzes."""
        user = User.objects.create_user(
            username="quiz_user",
            password="StrongPass123!",
        )
        quiz = Quiz.objects.create(
            user=user,
            title="Python Basics",
            description="An introduction to Python.",
            video_url="https://www.youtube.com/watch?v=example",
        )
        self.client.force_authenticate(user=user)

        response = self.client.get(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Python Basics")
        self.assertEqual(
            response.data["description"],
            "An introduction to Python.",
        )

    def test_user_cannot_retrieve_another_users_quiz(self):
        """Prevent users from retrieving quizzes owned by others."""
        owner = User.objects.create_user(
            username="quiz_owner",
            password="StrongPass123!",
        )
        other_user = User.objects.create_user(
            username="other_user",
            password="StrongPass123!",
        )
        quiz = Quiz.objects.create(
            user=owner,
            title="Private Quiz",
            description="Private description.",
            video_url="https://www.youtube.com/watch?v=example",
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.get(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_cannot_retrieve_quiz(self):
        """Require authentication before retrieving a quiz."""
        user = User.objects.create_user(
            username="quiz_owner",
            password="StrongPass123!",
        )
        quiz = Quiz.objects.create(
            user=user,
            title="Private Quiz",
            description="Private description.",
            video_url="https://www.youtube.com/watch?v=example",
        )

        response = self.client.get(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, 401)

    def test_user_cannot_retrieve_nonexistent_quiz(self):
        """Return 404 when the requested quiz does not exist."""
        user = User.objects.create_user(
            username="quiz_user",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/quizzes/999999/")

        self.assertEqual(response.status_code, 404)
