from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from quizzes.models import Question, Quiz


User = get_user_model()


class DeleteQuizTests(APITestCase):

    def test_user_can_delete_own_quiz(self):
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

        response = self.client.delete(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        self.assertFalse(Quiz.objects.filter(id=quiz.id).exists())
        self.assertFalse(
            Question.objects.filter(quiz_id=quiz.id).exists()
        )

    def test_user_cannot_delete_another_users_quiz(self):
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
            title="Python Basics",
            description="An introduction to Python.",
            video_url="https://www.youtube.com/watch?v=example",
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.delete(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Quiz.objects.filter(id=quiz.id).exists())

    def test_unauthenticated_user_cannot_delete_quiz(self):
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

        response = self.client.delete(f"/api/quizzes/{quiz.id}/")

        self.assertEqual(response.status_code, 401)
        self.assertTrue(Quiz.objects.filter(id=quiz.id).exists())

    def test_delete_nonexistent_quiz_returns_404(self):
        user = User.objects.create_user(
            username="quiz_user",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=user)

        response = self.client.delete("/api/quizzes/99999/")

        self.assertEqual(response.status_code, 404)
