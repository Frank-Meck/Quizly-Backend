
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from unittest.mock import patch

from quizzes.models import Question, Quiz


User = get_user_model()


class QuizModelTests(TestCase):

    def test_quiz_stores_owner_and_video_details(self):
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

        self.assertEqual(quiz.user, user)
        self.assertEqual(quiz.title, "Python Basics")
        self.assertEqual(
            quiz.description,
            "An introduction to Python.",
        )
        self.assertEqual(
            quiz.video_url,
            "https://www.youtube.com/watch?v=example",
        )
        self.assertIsNotNone(quiz.created_at)
        self.assertIsNotNone(quiz.updated_at)

    def test_quiz_question_stores_four_options_and_answer(self):
        user = User.objects.create_user(
            username="question_user",
            password="StrongPass123!",
        )
        quiz = Quiz.objects.create(
            user=user,
            title="Python Basics",
            description="Python questions",
            video_url="https://www.youtube.com/watch?v=example",
        )
        question = Question.objects.create(
            quiz=quiz,
            question_title="What is Python?",
            question_options=["Language", "Browser", "Database", "Editor"],
            answer="Language",
        )

        self.assertEqual(question.quiz, quiz)
        self.assertEqual(question.question_title, "What is Python?")
        self.assertEqual(len(question.question_options), 4)
        self.assertEqual(question.answer, "Language")
        self.assertIsNotNone(question.created_at)
        self.assertIsNotNone(question.updated_at)

class CreateQuizTests(APITestCase):

    def test_create_quiz_requires_authentication(self):
        response = self.client.post(
            "/api/quizzes/",
            {"url": "https://www.youtube.com/watch?v=example"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_create_quiz_requires_youtube_url(self):
        user = User.objects.create_user(
            username="quiz_user",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/quizzes/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_create_quiz_rejects_invalid_url(self):
        user = User.objects.create_user(
            username="quiz_user",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/quizzes/",
            {"url": "not-a-url"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_create_quiz_rejects_non_youtube_url(self):
        user = User.objects.create_user(
            username="quiz_user",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/quizzes/",
            {"url": "https://example.com/video"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_create_quiz_rejects_fake_youtube_domain(self):
        user = User.objects.create_user(
            username="quiz_user",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/quizzes/",
            {"url": "https://youtube.com.example.com/video"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)



    @patch("quizzes.views.generate_quiz_data", create=True)
    def test_create_quiz_accepts_valid_youtube_url(
        self,
        mock_generate_quiz_data,
    ):
        user = User.objects.create_user(
            username="quiz_user",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=user)

        mock_generate_quiz_data.return_value = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": f"Question {number}",
                    "question_options": [
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D",
                    ],
                    "answer": "Option A",
                }
                for number in range(1, 11)
            ],
        }

        response = self.client.post(
            "/api/quizzes/",
            {"url": "https://www.youtube.com/watch?v=example"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 10)
        mock_generate_quiz_data.assert_called_once_with(
            "https://www.youtube.com/watch?v=example"
        )
