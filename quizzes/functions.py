
"""Provide quiz generation, transcript extraction, and validation helpers."""

import html
import json
import logging
import os
import re
import shutil
import tempfile
import time
from pathlib import Path

import requests
import whisper
import yt_dlp
from google import genai
from google.genai import errors


logger = logging.getLogger(__name__)

_WHISPER_MODEL = None


QUIZ_PROMPT_TEMPLATE = """
Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{
    "title": "A concise quiz title based on the transcript.",
    "description": "A summary of no more than 150 characters.",
    "questions": [
        {
            "question_title": "The question goes here.",
            "question_options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": "The correct answer"
        }
    ]
}

Requirements:

- Generate exactly 10 questions.
- Generate the entire quiz in the same language as the transcript.
- Create a concise and relevant quiz title.
- Generate 3 easy questions.
- Generate 4 medium questions.
- Generate 3 difficult questions.
- Each question must have exactly 4 distinct options.
- Only one correct answer per question.
- Write clear and unambiguous questions.
- Use simple, natural language.
- The answer must be one of the four options.
- Create plausible but incorrect answer options.
- Use only information explicitly stated in the transcript.
- Do not introduce external knowledge or invent facts.
- Cover different aspects of the transcript.
- Do not repeat questions.
- Return valid JSON only, without explanations or Markdown.

Transcript:

{transcript}
"""


def validate_quiz_data(quiz_data):
    """Validate the structure and content of generated quiz data."""
    if not isinstance(quiz_data, dict):
        raise ValueError("Quiz data must be a dictionary.")

    title = quiz_data.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Quiz data must have a title.")

    description = quiz_data.get("description")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Quiz data must have a description.")

    if len(description) > 150:
        raise ValueError(
            "Quiz description must not exceed 150 characters."
        )

    questions = quiz_data.get("questions")
    if not isinstance(questions, list) or len(questions) != 10:
        raise ValueError(
            "Quiz data must contain exactly ten questions."
        )

    question_titles = set()

    for question in questions:
        _validate_question_data(question, question_titles)


def _validate_question_data(question, question_titles):
    """Validate one question and its answer options."""
    if not isinstance(question, dict):
        raise ValueError("Each question must be a dictionary.")

    question_title = question.get("question_title")
    if not isinstance(question_title, str) or not question_title.strip():
        raise ValueError("Each question must have a title.")

    if question_title in question_titles:
        raise ValueError("Quiz questions must be unique.")

    question_titles.add(question_title)
    options = question.get("question_options")

    if not isinstance(options, list) or len(options) != 4:
        raise ValueError("Each question must have four options.")

    if not all(
        isinstance(option, str) and option.strip()
        for option in options
    ):
        raise ValueError(
            "All question options must be non-empty strings."
        )

    if len(set(options)) != 4:
        raise ValueError("Question options must be unique.")

    if question.get("answer") not in options:
        raise ValueError("The answer must be one of the options.")


def clean_gemini_response(response):
    """Remove optional Markdown code fences from a Gemini response."""
    cleaned_response = response.strip()
    cleaned_response = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned_response,
        count=1,
        flags=re.IGNORECASE,
    )
    cleaned_response = re.sub(
        r"\s*```$",
        "",
        cleaned_response,
        count=1,
    )
    return cleaned_response.strip()


def generate_quiz_with_gemini(transcript):
    """Generate quiz data from a transcript using Gemini."""
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = QUIZ_PROMPT_TEMPLATE.replace("{transcript}", transcript)

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt,
            )
            cleaned_response = clean_gemini_response(response.text)
            return json.loads(cleaned_response)
        except errors.ServerError as error:
            if error.code != 503 or attempt == 2:
                raise

            logger.warning(
                "Gemini returned a temporary server error. Retrying."
            )
            time.sleep(2)


def generate_quiz_data(url):
    """Extract a video transcript and generate validated quiz data."""
    transcript = get_youtube_transcript(url)
    quiz_data = generate_quiz_with_gemini(transcript)
    validate_quiz_data(quiz_data)
    return quiz_data


def download_subtitle_text(url):
    """Download subtitle content from a subtitle URL."""
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.text


def clean_subtitle_text(subtitle_text):
    """Remove WebVTT metadata, timestamps, and markup."""
    text_lines = []

    for line in subtitle_text.splitlines():
        cleaned_line = line.strip()

        if _is_subtitle_metadata(cleaned_line):
            continue

        cleaned_line = re.sub(r"<[^>]+>", "", cleaned_line)
        cleaned_line = html.unescape(cleaned_line)

        if cleaned_line:
            text_lines.append(cleaned_line)

    return " ".join(text_lines)


def _is_subtitle_metadata(line):
    """Check whether a subtitle line contains metadata or a timestamp."""
    if not line or line == "WEBVTT":
        return True

    if re.match(
        r"^(?:\d{2}:)?\d{2}:\d{2}\.\d{3}\s+-->",
        line,
    ):
        return True

    if re.fullmatch(r"\d+", line):
        return True

    return line.startswith(("NOTE", "STYLE", "REGION"))


def download_youtube_audio(url):
    """Download YouTube audio into a temporary directory."""
    temp_dir = tempfile.mkdtemp(prefix="quizly_audio_")
    options = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(temp_dir, "audio.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "js_runtimes": {"node": {}},
    }

    try:
        audio_path = _download_audio_file(url, options)

        if not audio_path or not Path(audio_path).is_file():
            raise FileNotFoundError(
                "Downloaded audio file could not be found."
            )

        return audio_path, temp_dir
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def _download_audio_file(url, options):
    """Download audio and return the resulting file path."""
    with yt_dlp.YoutubeDL(options) as youtube_dl:
        info = youtube_dl.extract_info(url, download=True)
        downloads = info.get("requested_downloads") or []

        if downloads:
            return downloads[0].get("filepath")

        return youtube_dl.prepare_filename(info)


def transcribe_audio_with_whisper(audio_path):
    """Transcribe an audio file using the cached Whisper base model."""
    global _WHISPER_MODEL

    if _WHISPER_MODEL is None:
        logger.info("Loading the Whisper base model.")
        _WHISPER_MODEL = whisper.load_model("base")

    logger.info("Starting audio transcription.")
    result = _WHISPER_MODEL.transcribe(audio_path, fp16=False)
    transcript = result.get("text", "").strip()

    if not transcript:
        raise ValueError("Whisper could not generate a transcript.")

    logger.info("Audio transcription completed successfully.")
    return transcript


def get_transcript_from_audio(url):
    """Download YouTube audio and transcribe it with Whisper."""
    audio_path = None
    temp_dir = None

    try:
        logger.info("No usable subtitles found. Falling back to Whisper.")
        audio_path, temp_dir = download_youtube_audio(url)
        return transcribe_audio_with_whisper(audio_path)
    finally:
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)


def get_youtube_transcript(url):
    """Retrieve YouTube subtitles or fall back to Whisper transcription."""
    video_url = url.split("&")[0]
    options = {
        "skip_download": True,
        "quiet": True,
        "noplaylist": True,
        "js_runtimes": {"node": {}},
    }

    with yt_dlp.YoutubeDL(options) as youtube_dl:
        info = youtube_dl.extract_info(video_url, download=False)

    transcript = _get_transcript_from_subtitles(info)

    if transcript:
        return transcript

    return get_transcript_from_audio(video_url)


def _get_transcript_from_subtitles(video_info):
    """Find and download German or English subtitles."""
    subtitles = video_info.get("subtitles") or {}
    automatic_captions = video_info.get("automatic_captions") or {}

    for language in ("de", "en"):
        tracks = subtitles.get(language) or []
        tracks = tracks or automatic_captions.get(language) or []
        transcript = _download_transcript_track(tracks, language)

        if transcript:
            return transcript

    return None


def _download_transcript_track(tracks, language):
    """Download and clean the preferred subtitle track."""
    if not tracks:
        return None

    sorted_tracks = sorted(
        tracks,
        key=lambda track: track.get("ext") != "vtt",
    )

    for track in sorted_tracks:
        subtitle_url = track.get("url")

        if not subtitle_url:
            continue

        try:
            logger.info("Downloading %s subtitles.", language)
            subtitle_text = download_subtitle_text(subtitle_url)
            transcript = clean_subtitle_text(subtitle_text)

            if transcript:
                logger.info("Subtitle transcript downloaded successfully.")
                return transcript
        except requests.RequestException:
            logger.exception("Subtitle download failed.")
        except Exception:
            logger.exception("An error occurred while processing subtitles.")

    return None
