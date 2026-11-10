"""Coordinate quiz generation from YouTube videos."""

from quizzes.services.gemini import generate_quiz_with_gemini
from quizzes.services.transcripts import get_youtube_transcript
from quizzes.services.validation import validate_quiz_data


def generate_quiz_data(url):
    """Extract a video transcript and generate validated quiz data."""
    transcript = get_youtube_transcript(url)
    quiz_data = generate_quiz_with_gemini(transcript)
    validate_quiz_data(quiz_data)
    return quiz_data