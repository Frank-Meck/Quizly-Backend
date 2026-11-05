from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from quizzes.models import Question, Quiz


User = get_user_model()


class UpdateQuizTests(APITestCase):

    def test_user_can_partially_update_own_quiz(self):
        user = User.objects.create_user(
            username="quiz_user",
            password="StrongPass123!",
        )
        quiz = Quiz.objects.create(
            user=user,
            title="Python Basics",
            description="Old description.",
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

        response = self.client.patch(
            f"/api/quizzes/{quiz.id}/",
            {
                "title": "Updated Python Basics",
                "description": "Updated description.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated Python Basics")
        self.assertEqual(
            response.data["description"],
            "Updated description.",
        )
        self.assertEqual(len(response.data["questions"]), 1)

        quiz.refresh_from_db()
        self.assertEqual(quiz.title, "Updated Python Basics")
        self.assertEqual(quiz.description, "Updated description.")

    def test_user_cannot_update_another_users_quiz(self):
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

        response = self.client.patch(
            f"/api/quizzes/{quiz.id}/",
            {"title": "Hacked Title"},
            format="json",
        )

        self.assertEqual(response.status_code, 404)

        quiz.refresh_from_db()
        self.assertEqual(quiz.title, "Private Quiz")

    def test_unauthenticated_user_cannot_update_quiz(self):
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

        response = self.client.patch(
            f"/api/quizzes/{quiz.id}/",
            {"title": "Updated Title"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_update_quiz_rejects_invalid_video_url(self):
        user = User.objects.create_user(
            username="quiz_owner",
            password="StrongPass123!",
        )
        quiz = Quiz.objects.create(
            user=user,
            title="Python Basics",
            description="Python description.",
            video_url="https://www.youtube.com/watch?v=example",
        )
        self.client.force_authenticate(user=user)

        response = self.client.patch(
            f"/api/quizzes/{quiz.id}/",
            {"video_url": "https://www.example.com/video"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        quiz.refresh_from_db()
        self.assertEqual(
            quiz.video_url,
            "https://www.youtube.com/watch?v=example",
        )

    def test_update_quiz_accepts_valid_youtube_url(self):
        user = User.objects.create_user(
            username="quiz_owner",
            password="StrongPass123!",
        )
        quiz = Quiz.objects.create(
            user=user,
            title="Python Basics",
            description="Python description.",
            video_url="https://www.youtube.com/watch?v=example",
        )
        self.client.force_authenticate(user=user)

        new_video_url = "https://youtu.be/newvideo"

        response = self.client.patch(
            f"/api/quizzes/{quiz.id}/",
            {"video_url": new_video_url},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["video_url"], new_video_url)

        quiz.refresh_from_db()
        self.assertEqual(quiz.video_url, new_video_url)