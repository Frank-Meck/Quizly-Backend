"""Test YouTube transcript extraction and subtitle processing."""

from unittest.mock import patch

from django.test import SimpleTestCase

from quizzes.services.transcripts import (
    _download_transcript_track,
    clean_subtitle_text,
    download_subtitle_text,
    get_youtube_transcript,
)


class GetYouTubeTranscriptTests(SimpleTestCase):
    """Test transcript extraction from YouTube subtitles."""

    @patch("quizzes.services.transcripts.yt_dlp.YoutubeDL")
    def test_extracts_transcript_from_subtitles(self, mock_youtube_dl):
        """Extract a transcript from manually provided subtitles."""
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
            "quizzes.services.transcripts.download_subtitle_text",
            return_value="Python is a programming language.",
        ):
            transcript = get_youtube_transcript(
                "https://www.youtube.com/watch?v=test"
            )

        self.assertEqual(
            transcript,
            "Python is a programming language.",
        )

    @patch("quizzes.services.transcripts.yt_dlp.YoutubeDL")
    def test_extracts_plain_text_from_subtitles(self, mock_youtube_dl):
        """Remove subtitle timestamps before returning the transcript."""
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
            "quizzes.services.transcripts.download_subtitle_text",
            return_value=subtitle_text,
        ):
            transcript = get_youtube_transcript(
                "https://www.youtube.com/watch?v=test"
            )

        self.assertEqual(
            transcript,
            "Python is a programming language. It is easy to learn.",
        )


class SubtitleHelperTests(SimpleTestCase):
    """Test downloading and cleaning subtitle text."""

    @patch("quizzes.services.transcripts.requests.get")
    def test_downloads_subtitle_text(self, mock_get):
        """Download subtitle content and check the HTTP response."""
        mock_response = mock_get.return_value
        mock_response.text = "WEBVTT\n\nHello world"

        result = download_subtitle_text(
            "https://example.com/subtitles.vtt"
        )

        self.assertEqual(result, "WEBVTT\n\nHello world")
        mock_get.assert_called_once_with(
            "https://example.com/subtitles.vtt",
            timeout=15,
        )
        mock_response.raise_for_status.assert_called_once()

    def test_removes_cue_numbers_and_metadata(self):
        """Remove VTT headers, cue numbers, and metadata."""
        subtitle_text = (
            "WEBVTT\n\n"
            "1\n"
            "00:00:01.000 --> 00:00:02.000\n"
            "NOTE this is metadata\n"
            "STYLE\n"
            "REGION\n"
            "Hello world\n"
        )

        result = clean_subtitle_text(subtitle_text)

        self.assertEqual(result, "Hello world")

    @patch("quizzes.services.transcripts.download_subtitle_text")
    def test_skips_tracks_without_subtitle_url(
        self,
        mock_download_subtitle_text,
    ):
        """Skip subtitle tracks without a URL."""
        tracks = [
            {"ext": "vtt"},
            {"ext": "json"},
        ]

        result = _download_transcript_track(tracks, "en")

        self.assertIsNone(result)
        mock_download_subtitle_text.assert_not_called()