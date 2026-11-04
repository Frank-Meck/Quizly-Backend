from django.test import SimpleTestCase
from unittest.mock import patch
from quizzes.functions import get_youtube_transcript
from quizzes.functions import validate_quiz_data


class ValidateQuizDataTests(SimpleTestCase):

    def test_rejects_question_with_fewer_than_four_options(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": ["Language", "Browser", "Database"],
                    "answer": "Language",
                }
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_answer_not_in_question_options(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": [
                        "Language",
                        "Browser",
                        "Database",
                        "Editor",
                    ],
                    "answer": "Operating system",
                }
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_quiz_with_fewer_than_ten_questions(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
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
                }
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_question_without_title(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_options": [
                        "Language",
                        "Browser",
                        "Database",
                        "Editor",
                    ],
                    "answer": "Language",
                }
                for _ in range(10)
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_quiz_without_title(self):
        quiz_data = {
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

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_quiz_without_description(self):
        quiz_data = {
            "title": "Python Basics",
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

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_question_that_is_not_a_dictionary(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": ["Invalid question"] + [
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
                for number in range(2, 11)
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_duplicate_question_options(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": f"Question {number}",
                    "question_options": [
                        "Option A",
                        "Option A",
                        "Option C",
                        "Option D",
                    ],
                    "answer": "Option A",
                }
                for number in range(1, 11)
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_non_string_question_options(self):
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
                        123,
                    ],
                    "answer": "Option A",
                }
                for number in range(1, 11)
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)


    def test_rejects_description_longer_than_150_characters(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "A" * 151,
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

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)



    def test_accepts_description_with_exactly_150_characters(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "A" * 150,
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

        try:
            validate_quiz_data(quiz_data)
        except ValueError:
            self.fail("A 150-character description should be valid.")



    def test_rejects_duplicate_questions(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": (
                        "What is Python?"
                        if number == 1
                        else f"What is question {number}?"
                    ),
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

        quiz_data["questions"][1]["question_title"] = (
            quiz_data["questions"][0]["question_title"]
        )

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)


    def test_rejects_empty_description(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "   ",
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

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

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


class GetYouTubeTranscriptTests(SimpleTestCase):

    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    def test_extracts_transcript_from_subtitles(
        self,
        mock_youtube_dl,
    ):
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.return_value = {
            "subtitles": {
                "en": [{"url": "https://example.com/subtitles.vtt"}],
            },
            "automatic_captions": {},
        }

        with patch(
            "quizzes.functions.download_subtitle_text",
            return_value="Python is a programming language.",
            create=True,
        ):
            transcript = get_youtube_transcript(
                "https://www.youtube.com/watch?v=test"
            )

        self.assertEqual(
            transcript,
            "Python is a programming language.",
        )

    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    def test_extracts_plain_text_from_subtitles(
        self,
        mock_youtube_dl,
    ):
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.return_value = {
            "subtitles": {
                "en": [{"url": "https://example.com/subtitles.vtt"}],
            },
            "automatic_captions": {},
        }

        subtitle_text = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "Python is a programming language.\n\n"
            "00:00:03.000 --> 00:00:05.000\n"
            "It is easy to learn.\n"
        )

        with patch(
            "quizzes.functions.download_subtitle_text",
            return_value=subtitle_text,
        ):
            transcript = get_youtube_transcript(
                "https://www.youtube.com/watch?v=test"
            )

        self.assertEqual(
            transcript,
            "Python is a programming language. It is easy to learn.",
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


class WhisperTranscriptionTests(SimpleTestCase):

    def setUp(self):
        import quizzes.functions as quiz_functions

        self.quiz_functions = quiz_functions
        self.original_model = quiz_functions._WHISPER_MODEL
        quiz_functions._WHISPER_MODEL = None

    def tearDown(self):
        self.quiz_functions._WHISPER_MODEL = self.original_model

    @patch("quizzes.functions.whisper.load_model")
    def test_transcribes_audio_with_base_model(self, mock_load_model):
        mock_model = mock_load_model.return_value
        mock_model.transcribe.return_value = {
            "text": "  Python is a programming language.  "
        }

        result = self.quiz_functions.transcribe_audio_with_whisper(
            "test-audio.mp3"
        )

        mock_load_model.assert_called_once_with("base")
        mock_model.transcribe.assert_called_once_with(
            "test-audio.mp3",
            fp16=False,
        )
        self.assertEqual(result, "Python is a programming language.")

    @patch("quizzes.functions.whisper.load_model")
    def test_reuses_cached_whisper_model(self, mock_load_model):
        mock_model = mock_load_model.return_value
        mock_model.transcribe.return_value = {"text": "Test transcript"}

        self.quiz_functions.transcribe_audio_with_whisper("first.mp3")
        self.quiz_functions.transcribe_audio_with_whisper("second.mp3")

        mock_load_model.assert_called_once_with("base")
        self.assertEqual(mock_model.transcribe.call_count, 2)


class YouTubeAudioFallbackTests(SimpleTestCase):

    @patch("quizzes.functions.get_transcript_from_audio")
    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    def test_uses_whisper_when_no_subtitles_are_available(
        self,
        mock_youtube_dl,
        mock_get_audio_transcript,
    ):
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.return_value = {
            "subtitles": {},
            "automatic_captions": {},
        }

        mock_get_audio_transcript.return_value = (
            "Transcript generated with Whisper."
        )

        result = get_youtube_transcript(
            "https://www.youtube.com/watch?v=test"
        )

        self.assertEqual(
            result,
            "Transcript generated with Whisper.",
        )
        mock_get_audio_transcript.assert_called_once()

    @patch("quizzes.functions.get_transcript_from_audio")
    @patch("quizzes.functions.download_subtitle_text")
    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    def test_uses_whisper_when_subtitle_download_fails(
        self,
        mock_youtube_dl,
        mock_download_subtitle,
        mock_get_audio_transcript,
    ):
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.return_value = {
            "subtitles": {
                "en": [{"url": "https://example.com/subtitles.vtt"}]
            },
            "automatic_captions": {},
        }

        mock_download_subtitle.side_effect = Exception(
            "Subtitle download failed"
        )
        mock_get_audio_transcript.return_value = (
            "Transcript generated with Whisper."
        )

        result = get_youtube_transcript(
            "https://www.youtube.com/watch?v=test"
        )

        self.assertEqual(
            result,
            "Transcript generated with Whisper.",
        )
        mock_get_audio_transcript.assert_called_once()

    @patch("quizzes.functions.get_transcript_from_audio")
    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    def test_prefers_available_subtitles_over_whisper(
        self,
        mock_youtube_dl,
        mock_get_audio_transcript,
    ):
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.return_value = {
            "subtitles": {
                "en": [{"url": "https://example.com/subtitles.vtt"}]
            },
            "automatic_captions": {},
        }

        with patch(
            "quizzes.functions.download_subtitle_text",
            return_value="Subtitles are available.",
        ):
            result = get_youtube_transcript(
                "https://www.youtube.com/watch?v=test"
            )

        self.assertEqual(result, "Subtitles are available.")
        mock_get_audio_transcript.assert_not_called()


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
