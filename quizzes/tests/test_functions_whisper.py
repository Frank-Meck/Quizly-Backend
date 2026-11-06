
"""Test Whisper transcription and YouTube audio processing."""

import shutil
from unittest.mock import patch

import requests
from django.test import SimpleTestCase

import quizzes.functions as quiz_functions
from quizzes.functions import get_youtube_transcript


class WhisperTranscriptionTests(SimpleTestCase):
    """Test audio transcription using the Whisper model."""

    def setUp(self):
        """Reset the cached Whisper model before each test."""
        self.original_model = quiz_functions._WHISPER_MODEL
        quiz_functions._WHISPER_MODEL = None

    def tearDown(self):
        """Restore the original cached Whisper model."""
        quiz_functions._WHISPER_MODEL = self.original_model

    @patch("quizzes.functions.whisper.load_model")
    def test_transcribes_audio_with_base_model(self, mock_load_model):
        """Load the base model and return the cleaned transcript."""
        mock_model = mock_load_model.return_value
        mock_model.transcribe.return_value = {
            "text": "  Python is a programming language.  "
        }

        result = quiz_functions.transcribe_audio_with_whisper(
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
        """Reuse the loaded model for subsequent transcriptions."""
        mock_model = mock_load_model.return_value
        mock_model.transcribe.return_value = {
            "text": "Test transcript"
        }

        quiz_functions.transcribe_audio_with_whisper("first.mp3")
        quiz_functions.transcribe_audio_with_whisper("second.mp3")

        mock_load_model.assert_called_once_with("base")
        self.assertEqual(mock_model.transcribe.call_count, 2)

    @patch("quizzes.functions.whisper.load_model")
    def test_raises_error_when_transcription_is_empty(
        self,
        mock_load_model,
    ):
        """Raise an error when Whisper returns an empty transcript."""
        mock_model = mock_load_model.return_value
        mock_model.transcribe.return_value = {"text": "   "}

        with self.assertRaisesMessage(
            ValueError,
            "Whisper could not generate a transcript.",
        ):
            quiz_functions.transcribe_audio_with_whisper(
                "test-audio.mp3"
            )


class YouTubeAudioFallbackTests(SimpleTestCase):
    """Test fallback to Whisper when YouTube subtitles are unavailable."""

    @patch("quizzes.functions.get_transcript_from_audio")
    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    def test_uses_whisper_when_no_subtitles_are_available(
        self,
        mock_youtube_dl,
        mock_get_audio_transcript,
    ):
        """Use Whisper when no subtitles are available."""
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
        """Use Whisper when downloading subtitles fails."""
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.return_value = {
            "subtitles": {
                "en": [{"url": "https://example.com/subtitles.vtt"}],
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
    @patch("quizzes.functions.download_subtitle_text")
    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    def test_uses_whisper_when_subtitle_request_fails(
        self,
        mock_youtube_dl,
        mock_download_subtitle,
        mock_get_audio_transcript,
    ):
        """Use Whisper when the subtitle request raises an error."""
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.return_value = {
            "subtitles": {
                "en": [{"url": "https://example.com/subtitles.vtt"}],
            },
            "automatic_captions": {},
        }
        mock_download_subtitle.side_effect = requests.RequestException(
            "Network error"
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
        """Prefer available subtitles instead of transcribing audio."""
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
            return_value="Subtitles are available.",
        ):
            result = get_youtube_transcript(
                "https://www.youtube.com/watch?v=test"
            )

        self.assertEqual(result, "Subtitles are available.")
        mock_get_audio_transcript.assert_not_called()


class AudioDownloadTests(SimpleTestCase):
    """Test downloading and validating YouTube audio files."""

    @patch("quizzes.functions.Path.is_file", return_value=True)
    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    @patch(
        "quizzes.functions.tempfile.mkdtemp",
        return_value="test-temp-dir",
    )
    def test_downloads_audio_using_requested_filepath(
        self,
        mock_mkdtemp,
        mock_youtube_dl,
        mock_is_file,
    ):
        """Return the requested audio filepath after downloading."""
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.return_value = {
            "requested_downloads": [
                {"filepath": "test-audio.mp3"}
            ]
        }

        result = quiz_functions.download_youtube_audio(
            "https://youtube.com/watch?v=test"
        )

        self.assertEqual(
            result,
            ("test-audio.mp3", "test-temp-dir"),
        )
        mock_mkdtemp.assert_called_once()
        mock_instance.extract_info.assert_called_once()

    @patch("quizzes.functions.Path.is_file", return_value=True)
    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    @patch(
        "quizzes.functions.tempfile.mkdtemp",
        return_value="test-temp-dir",
    )
    def test_uses_prepared_filename_when_no_requested_downloads(
        self,
        mock_mkdtemp,
        mock_youtube_dl,
        mock_is_file,
    ):
        """Use the prepared filename when no filepath is provided."""
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.return_value = {
            "requested_downloads": []
        }
        mock_instance.prepare_filename.return_value = (
            "prepared-audio.mp3"
        )

        result = quiz_functions.download_youtube_audio(
            "https://youtube.com/watch?v=test"
        )

        self.assertEqual(
            result,
            ("prepared-audio.mp3", "test-temp-dir"),
        )
        mock_instance.prepare_filename.assert_called_once()

    @patch("shutil.rmtree")
    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    @patch(
        "quizzes.functions.tempfile.mkdtemp",
        return_value="test-temp-dir",
    )
    def test_removes_temp_directory_when_download_fails(
        self,
        mock_mkdtemp,
        mock_youtube_dl,
        mock_rmtree,
    ):
        """Remove temporary files when the download fails."""
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.side_effect = Exception(
            "Download failed"
        )

        with self.assertRaisesMessage(
            Exception,
            "Download failed",
        ):
            quiz_functions.download_youtube_audio(
                "https://youtube.com/watch?v=test"
            )

        mock_rmtree.assert_called_once_with(
            "test-temp-dir",
            ignore_errors=True,
        )

    @patch("shutil.rmtree")
    @patch("quizzes.functions.Path.is_file", return_value=False)
    @patch("quizzes.functions.yt_dlp.YoutubeDL")
    @patch(
        "quizzes.functions.tempfile.mkdtemp",
        return_value="test-temp-dir",
    )
    def test_raises_error_when_downloaded_file_does_not_exist(
        self,
        mock_mkdtemp,
        mock_youtube_dl,
        mock_is_file,
        mock_rmtree,
    ):
        """Raise an error when the downloaded file is missing."""
        mock_instance = (
            mock_youtube_dl.return_value.__enter__.return_value
        )
        mock_instance.extract_info.return_value = {
            "requested_downloads": [
                {"filepath": "missing-audio.mp3"}
            ]
        }

        with self.assertRaisesMessage(
            FileNotFoundError,
            "Downloaded audio file could not be found.",
        ):
            quiz_functions.download_youtube_audio(
                "https://youtube.com/watch?v=test"
            )

        mock_is_file.assert_called_once()
        mock_rmtree.assert_called_once_with(
            "test-temp-dir",
            ignore_errors=True,
        )


class AudioTranscriptTests(SimpleTestCase):
    """Test transcription and cleanup of downloaded audio."""

    @patch("shutil.rmtree")
    @patch("quizzes.functions.transcribe_audio_with_whisper")
    @patch("quizzes.functions.download_youtube_audio")
    def test_transcribes_audio_and_removes_temp_directory(
        self,
        mock_download,
        mock_transcribe,
        mock_rmtree,
    ):
        """Transcribe downloaded audio and remove temporary files."""
        mock_download.return_value = (
            "test-audio.mp3",
            "test-temp-dir",
        )
        mock_transcribe.return_value = "Test transcript"

        result = quiz_functions.get_transcript_from_audio(
            "https://youtube.com/watch?v=test"
        )

        self.assertEqual(result, "Test transcript")
        mock_transcribe.assert_called_once_with("test-audio.mp3")
        mock_rmtree.assert_called_once_with(
            "test-temp-dir",
            ignore_errors=True,
        )

    @patch("shutil.rmtree")
    @patch("quizzes.functions.transcribe_audio_with_whisper")
    @patch("quizzes.functions.download_youtube_audio")
    def test_removes_temp_directory_when_transcription_fails(
        self,
        mock_download,
        mock_transcribe,
        mock_rmtree,
    ):
        """Remove temporary files when transcription fails."""
        mock_download.return_value = (
            "test-audio.mp3",
            "test-temp-dir",
        )
        mock_transcribe.side_effect = ValueError(
            "Transcription failed"
        )

        with self.assertRaisesMessage(
            ValueError,
            "Transcription failed",
        ):
            quiz_functions.get_transcript_from_audio(
                "https://youtube.com/watch?v=test"
            )

        mock_rmtree.assert_called_once_with(
            "test-temp-dir",
            ignore_errors=True,
        )
