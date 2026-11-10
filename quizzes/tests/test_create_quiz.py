"""Test quiz models, serializers, and API creation."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

from quizzes.models import Question, Quiz
from quizzes.api.serializers import (
    CreateQuizDataSerializer,
    CreateQuizSerializer,
    QuizSerializer,
)


User = get_user_model()


class QuizPersistenceTests(TestCase):
    """Test storing quizzes and their associated questions."""

    def test_quiz_stores_owner_and_video_details(self):
        """Store the quiz owner, video details, and timestamps."""
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

    def test_question_stores_four_options_and_answer(self):
        """Store a question with four options and its correct answer."""
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
            question_options=[
                "Language",
                "Browser",
                "Database",
                "Editor",
            ],
            answer="Language",
        )

        self.assertEqual(question.quiz, quiz)
        self.assertEqual(question.question_title, "What is Python?")
        self.assertEqual(len(question.question_options), 4)
        self.assertEqual(question.answer, "Language")
        self.assertIsNotNone(question.created_at)
        self.assertIsNotNone(question.updated_at)


class CreateQuizSerializerTests(TestCase):
    """Test validation and creation of quiz serializer data."""

    def test_serializer_accepts_valid_youtube_url(self):
        """Accept a valid YouTube URL."""
        serializer = CreateQuizSerializer(
            data={
                "url": "https://www.youtube.com/watch?v=example",
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_serializer_rejects_non_youtube_url(self):
        """Reject URLs that do not belong to YouTube."""
        serializer = CreateQuizSerializer(
            data={
                "url": "https://example.com/video",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("url", serializer.errors)

    def test_serializer_creates_quiz_with_questions(self):
        """Create a quiz and its questions using the serializer."""
        user = User.objects.create_user(
            username="serializer_user",
            password="StrongPass123!",
        )
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "video_url": "https://www.youtube.com/watch?v=example",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": [
                        "Language",
                        "Browser",
                        "Database",
                        "Editor",
                    ],
                    "answer": "Language",
                },
            ],
        }

        serializer = CreateQuizDataSerializer(data=quiz_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

        quiz = serializer.save(user=user)

        self.assertEqual(quiz.user, user)
        self.assertEqual(quiz.title, "Python Basics")
        self.assertEqual(quiz.questions.count(), 1)
        self.assertEqual(
            quiz.questions.first().question_title,
            "What is Python?",
        )

    def test_serializer_rejects_question_without_answer(self):
        """Reject questions that do not contain a correct answer."""
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "video_url": "https://www.youtube.com/watch?v=example",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": [
                        "Language",
                        "Browser",
                        "Database",
                        "Editor",
                    ],
                },
            ],
        }

        serializer = CreateQuizDataSerializer(data=quiz_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("questions", serializer.errors)

    def test_serializer_rejects_wrong_number_of_options(self):
        """Reject questions that do not contain exactly four options."""
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "video_url": "https://www.youtube.com/watch?v=example",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": [
                        "Language",
                        "Browser",
                    ],
                    "answer": "Language",
                },
            ],
        }

        serializer = CreateQuizDataSerializer(data=quiz_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("questions", serializer.errors)

    def test_serializer_rejects_empty_question_options(self):
        """Reject answer options that are empty or not strings."""
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "video_url": "https://www.youtube.com/watch?v=example",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": [
                        "Language",
                        "",
                        "Database",
                        "Editor",
                    ],
                    "answer": "Language",
                },
            ],
        }

        serializer = CreateQuizDataSerializer(data=quiz_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("questions", serializer.errors)

    def test_serializer_rejects_duplicate_question_options(self):
        """Reject answer options that are not unique."""
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "video_url": "https://www.youtube.com/watch?v=example",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": [
                        "Language",
                        "Browser",
                        " Language ",
                        "Editor",
                    ],
                    "answer": "Language",
                },
            ],
        }

        serializer = CreateQuizDataSerializer(data=quiz_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("questions", serializer.errors)

    def test_serializer_rejects_answer_not_in_options(self):
        """Reject answers that are not included in the options."""
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "video_url": "https://www.youtube.com/watch?v=example",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": [
                        "Language",
                        "Browser",
                        "Database",
                        "Editor",
                    ],
                    "answer": "Java",
                },
            ],
        }

        serializer = CreateQuizDataSerializer(data=quiz_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("questions", serializer.errors)

    def test_quiz_serializer_has_no_custom_create_method(self):
        """Ensure the read-only quiz serializer has no custom create method."""
        self.assertNotIn("create", QuizSerializer.__dict__)

    def test_quiz_serializer_questions_are_read_only(self):
        """Ensure questions cannot be modified through the quiz serializer."""
        serializer = QuizSerializer()

        self.assertTrue(serializer.fields["questions"].read_only)


class CreateQuizTests(APITestCase):
    """Test the API endpoint for creating quizzes."""

    def test_create_quiz_requires_authentication(self):
        """Reject quiz creation requests from unauthenticated users."""
        response = self.client.post(
            "/api/quizzes/",
            {"url": "https://www.youtube.com/watch?v=example"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_create_quiz_requires_youtube_url(self):
        """Reject requests without a URL."""
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
        """Reject malformed URLs."""
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
        """Reject URLs from domains other than YouTube."""
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
        """Reject URLs that only contain YouTube in another domain."""
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

    @patch("quizzes.api.views.generate_quiz_data")
    def test_create_quiz_accepts_valid_youtube_url(
        self,
        mock_generate_quiz_data,
    ):
        """Create and save a quiz from a valid YouTube URL."""
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

        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["title"], "Python Basics")
        self.assertEqual(
            response.data["video_url"],
            "https://www.youtube.com/watch?v=example",
        )
        self.assertEqual(len(response.data["questions"]), 10)
        self.assertEqual(
            response.data["questions"][0]["question_title"],
            "Question 1",
        )

        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(Question.objects.count(), 10)
        mock_generate_quiz_data.assert_called_once_with(
            "https://www.youtube.com/watch?v=example"
        )

    @patch("quizzes.api.views.generate_quiz_data")
    @patch("quizzes.api.views.CreateQuizDataSerializer")
    def test_create_quiz_uses_create_quiz_data_serializer(
        self,
        mock_serializer_class,
        mock_generate_quiz_data,
    ):
        """Use the quiz data serializer to validate generated quiz data."""
        user = User.objects.create_user(
            username="serializer_user",
            password="StrongPass123!",
        )
        self.client.force_authenticate(user=user)

        mock_generate_quiz_data.return_value = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [],
        }

        mock_serializer = mock_serializer_class.return_value
        mock_serializer.is_valid.return_value = True
        mock_serializer.save.return_value = Quiz(
            pk=1,
            user=user,
            title="Python Basics",
            description="An introduction to Python.",
            video_url="https://www.youtube.com/watch?v=example",
        )
        mock_serializer.data = {
            "id": 1,
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "video_url": "https://www.youtube.com/watch?v=example",
            "questions": [],
        }

        response = self.client.post(
            "/api/quizzes/",
            {"url": "https://www.youtube.com/watch?v=example"},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        mock_generate_quiz_data.assert_called_once_with(
            "https://www.youtube.com/watch?v=example"
        )
        mock_serializer_class.assert_called_once()
        mock_serializer.is_valid.assert_called_once_with(
            raise_exception=True
        )
        mock_serializer.save.assert_called_once_with(user=user)
