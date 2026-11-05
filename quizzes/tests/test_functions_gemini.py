from unittest.mock import patch
from django.test import SimpleTestCase


class GenerateQuizDataTests(SimpleTestCase):

    @patch(
        "quizzes.functions.get_youtube_transcript",
        create=True,
    )
    @patch(
        "quizzes.functions.generate_quiz_with_gemini",
        create=True,
    )
    def test_generates_and_validates_quiz(
        self,
        mock_generate_quiz,
        mock_get_transcript,
    ):
        from quizzes.functions import generate_quiz_data

        mock_get_transcript.return_value = "Python is a programming language."
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

        result = generate_quiz_data("https://www.youtube.com/watch?v=test")

        self.assertEqual(result["title"], "Python Basics")
        mock_get_transcript.assert_called_once_with(
            "https://www.youtube.com/watch?v=test"
        )


class GenerateQuizWithGeminiTests(SimpleTestCase):

    @patch("quizzes.functions.genai.Client")
    def test_generates_quiz_from_transcript(self, mock_client):
        from quizzes.functions import generate_quiz_with_gemini

        transcript = "Python is a programming language."
        expected_quiz = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [],
        }

        mock_response = mock_client.return_value.models.generate_content
        mock_response.return_value.text = (
            '{"title": "Python Basics", '
            '"description": "An introduction to Python.", '
            '"questions": []}'
        )

        result = generate_quiz_with_gemini(transcript)

        self.assertEqual(result, expected_quiz)
        mock_response.assert_called_once()
        self.assertEqual(
            mock_response.call_args.kwargs["model"],
            "gemini-3.5-flash-lite",
        )

    @patch("quizzes.functions.genai.Client")
    def test_parses_markdown_json_response(self, mock_client):
        from quizzes.functions import generate_quiz_with_gemini

        transcript = "Python is a programming language."
        expected_quiz = {"title": "Python Basics"}

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = (
            '```json\n'
            '{"title": "Python Basics"}\n'
            '```'
        )

        result = generate_quiz_with_gemini(transcript)

        self.assertEqual(result, expected_quiz)



    @patch("quizzes.functions.genai.Client")
    def test_includes_transcript_in_prompt(self, mock_client):
        from quizzes.functions import generate_quiz_with_gemini

        transcript = "Python supports object-oriented programming."

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = '{"title": "Python Basics"}'

        generate_quiz_with_gemini(transcript)

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(transcript, prompt)



    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_transcript_only_information(
        self,
        mock_client,
    ):
        from quizzes.functions import generate_quiz_with_gemini

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = '{"title": "Python Basics"}'

        generate_quiz_with_gemini("Python is a programming language.")

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
        from quizzes.functions import generate_quiz_with_gemini

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = '{"title": "Python Basics"}'

        generate_quiz_with_gemini("Python is a programming language.")

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
        from quizzes.functions import generate_quiz_with_gemini

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = '{"title": "Python Basics"}'

        generate_quiz_with_gemini("Python is a programming language.")

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
        from quizzes.functions import generate_quiz_with_gemini

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = '{"title": "Python Basics"}'

        generate_quiz_with_gemini("Python is a programming language.")

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn("3 easy questions", prompt)
        self.assertIn("4 medium questions", prompt)
        self.assertIn("3 difficult questions", prompt)

    @patch("quizzes.functions.genai.Client")
    def test_prompt_requires_clear_and_unambiguous_questions(
        self,
        mock_client,
    ):
        from quizzes.functions import generate_quiz_with_gemini

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = '{"title": "Python Basics"}'

        generate_quiz_with_gemini("Python is a programming language.")

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
        from quizzes.functions import generate_quiz_with_gemini

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = '{"title": "Python Basics"}'

        generate_quiz_with_gemini("Python is a programming language.")

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
        from quizzes.functions import generate_quiz_with_gemini

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = '{"title": "Python Basics"}'

        generate_quiz_with_gemini("Python is a programming language.")

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
        from quizzes.functions import generate_quiz_with_gemini

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = '{"title": "Python Basics"}'

        generate_quiz_with_gemini("Python ist eine Programmiersprache.")

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
        from quizzes.functions import generate_quiz_with_gemini

        mock_response = (
            mock_client.return_value.models.generate_content
        )
        mock_response.return_value.text = '{"title": "Python Basics"}'

        generate_quiz_with_gemini("Python is a programming language.")

        prompt = mock_response.call_args.kwargs["contents"]

        self.assertIn(
            "Create a concise and relevant quiz title",
            prompt,
        )


class CleanGeminiResponseTests(SimpleTestCase):

    def test_removes_json_markdown_code_block(self):
        from quizzes.functions import clean_gemini_response

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
        from quizzes.functions import clean_gemini_response

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
        import json

        from quizzes.functions import clean_gemini_response

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

    @patch("quizzes.functions.generate_quiz_with_gemini")
    @patch("quizzes.functions.get_youtube_transcript")
    def test_rejects_invalid_quiz_returned_by_gemini(
        self,
        mock_get_transcript,
        mock_generate_quiz,
    ):
        from quizzes.functions import generate_quiz_data

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
