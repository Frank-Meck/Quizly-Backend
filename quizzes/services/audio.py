"""Download YouTube audio and transcribe it with Whisper."""

import logging
import os
import shutil
import tempfile
from pathlib import Path

import whisper
import yt_dlp


logger = logging.getLogger(__name__)

_WHISPER_MODEL = None


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