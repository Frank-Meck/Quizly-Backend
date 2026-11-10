"""Extract and clean transcripts from YouTube videos."""

import html
import logging
import re

import requests
import yt_dlp

from quizzes.services.audio import get_transcript_from_audio


logger = logging.getLogger(__name__)


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
            logger.exception(
                "An error occurred while processing subtitles."
            )

    return None