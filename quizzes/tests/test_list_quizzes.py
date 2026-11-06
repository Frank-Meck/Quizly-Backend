
"""Test listing quizzes through the API."""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from quizzes.models import Question, Quiz


User = get_user_model()


class ListQuizzesTests(APITestCase):
    """Test retrieving quizzes belonging to the authenticated user."""

    def test_user_can_list_own_quizzes(self):
        """Return the user's quizzes together with their questions."""
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
        self.client.force_authenticate(user=user)

        response = self.client.get("/api/quizzes/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Python Basics")
        self.assertEqual(len(response.data[0]["questions"]), 1)

    def test_user_cannot_list_another_users_quizzes(self):
        """Do not expose quizzes belonging to other users."""
        owner = User.objects.create_user(
            username="quiz_owner",
            password="StrongPass123!",
        )
        other_user = User.objects.create_user(
            username="other_user",
            password="StrongPass123!",
        )
        Quiz.objects.create(
            user=owner,
            title="Private Quiz",
            description="Private description.",
            video_url="https://www.youtube.com/watch?v=example",
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.get("/api/quizzes/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_unauthenticated_user_cannot_list_quizzes(self):
        """Require authentication before listing quizzes."""
        response = self.client.get("/api/quizzes/")

        self.assertEqual(response.status_code, 401)
