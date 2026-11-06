
"""Test Gemini quiz generation and response handling."""

import json
from unittest.mock import patch

from django.test import SimpleTestCase

from quizzes.functions import (
    clean_gemini_response,
    generate_quiz_data,
    generate_quiz_with_gemini,
)


class MockServerError(Exception):
    """Simulate a Gemini server error with an HTTP status code."""

    def __init__(self, code):
        self.code = code


class GenerateQuizDataTests(SimpleTestCase):
    """Test quiz generation and validation using Gemini."""

    @patch("quizzes.functions.get_youtube_transcript")
    @patch("quizzes.functions.generate_quiz_with_gemini")
    def test_generates_and_validates_quiz(
        self,
        mock_generate_quiz,
        mock_get_transcript,
    ):
        """Generate and validate quiz data from a video transcript."""
        mock_get_transcript.return_value = (
            "Python is a programming language."
        )
        mock_generate_quiz.return_value = {
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

        result = generate_quiz_data(
            "https://www.youtube.com/watch?v=test"
        )

        self.assertEqual(result["title"], "Python Basics")
        mock_get_transcript.assert_called_once_with(
            "https://www.youtube.com/watch?v=test"
        )


class GenerateQuizWithGeminiTests(SimpleTestCase):
    """Test Gemini API requests, responses, and prompt instructions."""

    @patch("quizzes.functions.genai.Client")
    def test_generates_quiz_from_transcript(self, mock_client):
        """Generate quiz data from a transcript."""
        expected_quiz = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [],
        }
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics", '
            '"description": "An introduction to Python.", '
            '"questions": []}'
        )

        result = generate_quiz_with_gemini(
            "Python is a programming language."
        )

        self.assertEqual(result, expected_quiz)
        mock_response.assert_called_once()
        self.assertEqual(
            mock_response.call_args.kwargs["model"],
            "gemini-3.5-flash-lite",
        )

    @patch("quizzes.functions.genai.Client")
    def test_parses_markdown_json_response(self, mock_client):
        """Parse JSON returned inside a Markdown code block."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '```json\n'
            '{"title": "Python Basics"}\n'
            '```'
        )

        result = generate_quiz_with_gemini(
            "Python is a programming language."
        )

        self.assertEqual(result, {"title": "Python Basics"})

    @patch("quizzes.functions.time.sleep")
    @patch(
        "quizzes.functions.errors.ServerError",
        MockServerError,
    )
    @patch("quizzes.functions.genai.Client")
    def test_retries_after_temporary_server_error(
        self,
        mock_client,
        mock_sleep,
    ):
        """Retry after a 503 error and return the successful response."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.side_effect = [
            MockServerError(503),
            type(
                "Response",
                (),
                {"text": '{"title": "Python Basics"}'},
            )(),
        ]

        result = generate_quiz_with_gemini("Python transcript")

        self.assertEqual(result, {"title": "Python Basics"})
        self.assertEqual(mock_response.call_count, 2)
        mock_sleep.assert_called_once_with(2)

    @patch("quizzes.functions.time.sleep")
    @patch(
        "quizzes.functions.errors.ServerError",
        MockServerError,
    )
    @patch("quizzes.functions.genai.Client")
    def test_raises_error_after_three_failed_attempts(
        self,
        mock_client,
        mock_sleep,
    ):
        """Raise the server error after three unsuccessful attempts."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.side_effect = [
            MockServerError(503),
            MockServerError(503),
            MockServerError(503),
        ]

        with self.assertRaises(MockServerError):
            generate_quiz_with_gemini("Python transcript")

        self.assertEqual(mock_response.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("quizzes.functions.time.sleep")
    @patch(
        "quizzes.functions.errors.ServerError",
        MockServerError,
    )
    @patch("quizzes.functions.genai.Client")
    def test_does_not_retry_non_503_server_error(
        self,
        mock_client,
        mock_sleep,
    ):
        """Do not retry server errors other than HTTP 503."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.side_effect = MockServerError(500)

        with self.assertRaises(MockServerError):
            generate_quiz_with_gemini("Python transcript")

        mock_response.assert_called_once()
        mock_sleep.assert_not_called()

    @patch("quizzes.functions.genai.Client")
    def test_includes_transcript_in_prompt(self, mock_client):
        """Include the transcript in the Gemini prompt."""
        transcript = (
            "Python supports object-oriented programming."
        )
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics"}'
        )

        generate_quiz_with_gemini(transcript)

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(transcript, prompt)

    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_transcript_only_information(
        self,
        mock_client,
    ):
        """Require the quiz to use only transcript information."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics"}'
        )

        generate_quiz_with_gemini(
            "Python is a programming language."
        )

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(
            "Use only information explicitly stated in the transcript",
            prompt,
        )

    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_questions_about_different_aspects(
        self,
        mock_client,
    ):
        """Require questions about different transcript aspects."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics"}'
        )

        generate_quiz_with_gemini(
            "Python is a programming language."
        )

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(
            "Cover different aspects of the transcript",
            prompt,
        )

    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_plausible_answer_options(
        self,
        mock_client,
    ):
        """Require plausible but incorrect answer options."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics"}'
        )

        generate_quiz_with_gemini(
            "Python is a programming language."
        )

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(
            "plausible but incorrect answer options",
            prompt,
        )

    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_mixed_difficulty_levels(
        self,
        mock_client,
    ):
        """Require the specified distribution of difficulty levels."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics"}'
        )

        generate_quiz_with_gemini(
            "Python is a programming language."
        )

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn("3 easy questions", prompt)
        self.assertIn("4 medium questions", prompt)
        self.assertIn("3 difficult questions", prompt)

    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_clear_and_unambiguous_questions(
        self,
        mock_client,
    ):
        """Require clear and unambiguous questions."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics"}'
        )

        generate_quiz_with_gemini(
            "Python is a programming language."
        )

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(
            "Write clear and unambiguous questions",
            prompt,
        )

    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_simple_and_natural_language(
        self,
        mock_client,
    ):
        """Require simple and natural language."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics"}'
        )

        generate_quiz_with_gemini(
            "Python is a programming language."
        )

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(
            "Use simple, natural language",
            prompt,
        )

    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_no_repeated_question_content(
        self,
        mock_client,
    ):
        """Prevent repeated question content."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics"}'
        )

        generate_quiz_with_gemini(
            "Python is a programming language."
        )

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(
            "Do not repeat questions",
            prompt,
        )

    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_same_language_as_transcript(
        self,
        mock_client,
    ):
        """Require the quiz to use the transcript language."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics"}'
        )

        generate_quiz_with_gemini(
            "Python ist eine Programmiersprache."
        )

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(
            "Generate the entire quiz in the same language as the transcript",
            prompt,
        )

    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_concise_and_relevant_title(
        self,
        mock_client,
    ):
        """Require a concise and relevant quiz title."""
        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '{"title": "Python Basics"}'
        )

        generate_quiz_with_gemini(
            "Python is a programming language."
        )

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(
            "Create a concise and relevant quiz title",
            prompt,
        )


class CleanGeminiResponseTests(SimpleTestCase):
    """Test cleaning and parsing Gemini responses."""

    def test_removes_json_markdown_code_block(self):
        """Remove JSON Markdown code fences."""
        response = (
            '```json\n'
            '{"title": "Python Basics"}\n'
            '```'
        )

        result = clean_gemini_response(response)

        self.assertEqual(
            result,
            '{"title": "Python Basics"}',
        )

    def test_removes_plain_markdown_code_block(self):
        """Remove plain Markdown code fences."""
        response = (
            '```\n'
            '{"title": "Python Basics"}\n'
            '```'
        )

        result = clean_gemini_response(response)

        self.assertEqual(
            result,
            '{"title": "Python Basics"}',
        )

    def test_parses_cleaned_json_response(self):
        """Parse JSON after removing Markdown code fences."""
        response = (
            '```json\n'
            '{"title": "Python Basics"}\n'
            '```'
        )

        cleaned_response = clean_gemini_response(response)
        result = json.loads(cleaned_response)

        self.assertEqual(
            result,
            {"title": "Python Basics"},
        )


class GenerateQuizDataErrorTests(SimpleTestCase):
    """Test error handling during quiz generation."""

    @patch("quizzes.functions.generate_quiz_with_gemini")
    @patch("quizzes.functions.get_youtube_transcript")
    def test_rejects_invalid_quiz_returned_by_gemini(
        self,
        mock_get_transcript,
        mock_generate_quiz,
    ):
        """Reject invalid quiz data returned by Gemini."""
        mock_get_transcript.return_value = (
            "Python is a programming language."
        )
        mock_generate_quiz.return_value = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [],
        }

        with self.assertRaises(ValueError):
            generate_quiz_data(
                "https://www.youtube.com/watch?v=test"
            )
