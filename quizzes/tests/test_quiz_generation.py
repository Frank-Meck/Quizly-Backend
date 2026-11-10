"""Test the quiz generation workflow."""

from unittest.mock import call, patch

from django.test import SimpleTestCase

from quizzes.services.quiz_generation import generate_quiz_data


class GenerateQuizDataTests(SimpleTestCase):
    """Test quiz generation and validation."""

    @patch("quizzes.services.quiz_generation.get_youtube_transcript")
    @patch("quizzes.services.quiz_generation.generate_quiz_with_gemini")
    def test_generates_and_validates_quiz(
        self,
        mock_generate_quiz,
        mock_get_transcript,
    ):
        """Generate and validate quiz data from a video transcript."""
        transcript = "Python is a programming language."
        quiz_data = {
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

        mock_get_transcript.return_value = transcript
        mock_generate_quiz.return_value = quiz_data

        url = "https://www.youtube.com/watch?v=test"
        result = generate_quiz_data(url)

        self.assertEqual(result, quiz_data)
        self.assertEqual(
            mock_get_transcript.call_args_list,
            [call(url)],
        )
        mock_generate_quiz.assert_called_once_with(transcript)

    @patch("quizzes.services.quiz_generation.generate_quiz_with_gemini")
    @patch("quizzes.services.quiz_generation.get_youtube_transcript")
    def test_rejects_invalid_quiz_returned_by_gemini(
        self,
        mock_get_transcript,
        mock_generate_quiz,
    ):
        """Reject invalid quiz data returned by Gemini."""
        transcript = "Python is a programming language."
        mock_get_transcript.return_value = transcript
        mock_generate_quiz.return_value = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [],
        }

        with self.assertRaises(ValueError):
            generate_quiz_data(
                "https://www.youtube.com/watch?v=test"
            )

        mock_get_transcript.assert_called_once()
        mock_generate_quiz.assert_called_once_with(transcript)

    @patch("quizzes.services.quiz_generation.generate_quiz_with_gemini")
    @patch("quizzes.services.quiz_generation.get_youtube_transcript")
    def test_propagates_transcript_error(
        self,
        mock_get_transcript,
        mock_generate_quiz,
    ):
        """Propagate errors raised while retrieving the transcript."""
        mock_get_transcript.side_effect = RuntimeError(
            "Transcript retrieval failed."
        )

        with self.assertRaisesMessage(
            RuntimeError,
            "Transcript retrieval failed.",
        ):
            generate_quiz_data(
                "https://www.youtube.com/watch?v=test"
            )

        mock_generate_quiz.assert_not_called()

    @patch("quizzes.services.quiz_generation.generate_quiz_with_gemini")
    @patch("quizzes.services.quiz_generation.get_youtube_transcript")
    def test_propagates_gemini_error(
        self,
        mock_get_transcript,
        mock_generate_quiz,
    ):
        """Propagate errors raised while generating the quiz."""
        mock_get_transcript.return_value = (
            "Python is a programming language."
        )
        mock_generate_quiz.side_effect = RuntimeError(
            "Quiz generation failed."
        )

        with self.assertRaisesMessage(
            RuntimeError,
            "Quiz generation failed.",
        ):
            generate_quiz_data(
                "https://www.youtube.com/watch?v=test"
            )

        mock_get_transcript.assert_called_once()
        mock_generate_quiz.assert_called_once()
