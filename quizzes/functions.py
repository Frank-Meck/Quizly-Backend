
import re
import html
import json
import os
import tempfile
from pathlib import Path

import requests
import yt_dlp
import whisper
from google import genai


# Whisper-Modell zwischenspeichern
# Das Modell wird nur einmal geladen.
_WHISPER_MODEL = None


def validate_quiz_data(quiz_data):
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

    question_titles = [
        question.get("question_title")
        for question in questions
        if isinstance(question, dict)
    ]

    if len(question_titles) != len(set(question_titles)):
        raise ValueError("Quiz questions must be unique.")

    for question in questions:
        if not isinstance(question, dict):
            raise ValueError(
                "Each question must be a dictionary."
            )

        if not isinstance(question.get("question_title"), str):
            raise ValueError("Each question must have a title.")

        if not question["question_title"].strip():
            raise ValueError("Each question must have a title.")

        options = question.get("question_options")

        if not isinstance(options, list) or len(options) != 4:
            raise ValueError(
                "Each question must have four options."
            )

        if not all(
            isinstance(option, str) and option.strip()
            for option in options
        ):
            raise ValueError(
                "All question options must be non-empty strings."
            )

        if len(set(options)) != 4:
            raise ValueError(
                "Question options must be unique."
            )

        answer = question.get("answer")

        if answer not in options:
            raise ValueError(
                "The answer must be one of the options."
            )


def clean_gemini_response(response):
    response = response.strip()

    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        count=1,
    )

    response = re.sub(
        r"\s*```$",
        "",
        response,
        count=1,
    )

    return response.strip()


def generate_quiz_with_gemini(transcript):

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = f"""
Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:
{{
    "title": "A concise quiz title based on the transcript.",
    "description": "A summary of no more than 150 characters.",
    "questions": [
        {{
            "question_title": "The question goes here.",
            "question_options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D"
            ],
            "answer": "The correct answer"
        }}
    ]
}}

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

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    cleaned_response = clean_gemini_response(response.text)

    return json.loads(cleaned_response)


def generate_quiz_data(url):

    transcript = get_youtube_transcript(url)

    quiz_data = generate_quiz_with_gemini(transcript)

    validate_quiz_data(quiz_data)

    return quiz_data


def download_subtitle_text(url):

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    return response.text


def clean_subtitle_text(subtitle_text):

    lines = subtitle_text.splitlines()
    text_lines = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line == "WEBVTT":
            continue

        # Zeitangaben entfernen
        if re.match(
            r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->",
            line,
        ):
            continue

        # Nummerierte Untertitelblöcke entfernen
        if re.fullmatch(r"\d+", line):
            continue

        # VTT-Metadaten entfernen
        if line.startswith(("NOTE", "STYLE", "REGION")):
            continue

        # HTML- und Untertitel-Tags entfernen
        line = re.sub(r"<[^>]+>", "", line)

        # HTML-Sonderzeichen umwandeln
        line = html.unescape(line)

        if line:
            text_lines.append(line)

    return " ".join(text_lines)


def download_youtube_audio(url):

    # Temporären Ordner für die Audiodatei erstellen
    temp_dir = tempfile.mkdtemp(prefix="quizly_audio_")

    options = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(
            temp_dir,
            "audio.%(ext)s"
        ),
        "quiet": True,
        "noplaylist": True,
        "js_runtimes": {
            "node": {}
        },
    }

    try:
        with yt_dlp.YoutubeDL(options) as youtube_dl:

            info = youtube_dl.extract_info(
                url,
                download=True,
            )

            # Tatsächlichen Dateipfad ermitteln
            downloads = info.get("requested_downloads") or []

            if downloads:
                audio_path = downloads[0].get("filepath")
            else:
                audio_path = youtube_dl.prepare_filename(info)

        if not audio_path or not Path(audio_path).is_file():
            raise FileNotFoundError(
                "Downloaded audio file could not be found."
            )

        return audio_path, temp_dir

    except Exception:
        # Temporären Ordner bei einem Fehler aufräumen
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def transcribe_audio_with_whisper(audio_path):

    global _WHISPER_MODEL

    # Modell nur beim ersten Aufruf laden
    if _WHISPER_MODEL is None:

        print("WHISPER: Lade Modell base ...")

        _WHISPER_MODEL = whisper.load_model("base")

        print("WHISPER: Modell erfolgreich geladen.")

    print("WHISPER: Starte Transkription ...")

    result = _WHISPER_MODEL.transcribe(
        audio_path,
        fp16=False,
    )

    transcript = result.get("text", "").strip()

    if not transcript:
        raise ValueError(
            "Whisper could not generate a transcript."
        )

    print("WHISPER: Transkription erfolgreich.")

    return transcript


def get_transcript_from_audio(url):

    audio_path = None
    temp_dir = None

    try:
        print("QUIZLY: Keine passenden Untertitel gefunden.")
        print("QUIZLY: Wechsle zu Whisper.")

        audio_path, temp_dir = download_youtube_audio(url)

        transcript = transcribe_audio_with_whisper(
            audio_path
        )

        return transcript

    finally:
        # Audiodatei und temporären Ordner löschen
        if temp_dir:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


def get_youtube_transcript(url):

    url = url.split("&")[0]

    options = {
        "skip_download": True,
        "quiet": True,
        "noplaylist": True,
        "js_runtimes": {
            "node": {}
        },
    }

    with yt_dlp.YoutubeDL(options) as youtube_dl:

        info = youtube_dl.extract_info(
            url,
            download=False,
        )

    subtitles = info.get("subtitles") or {}

    automatic_captions = (
        info.get("automatic_captions") or {}
    )

    # Zuerst deutsche und englische Originaluntertitel suchen
    for language in ("de", "en"):

        tracks = subtitles.get(language) or []

        if not tracks:
            tracks = automatic_captions.get(language) or []

        if tracks:

            tracks = sorted(
                tracks,
                key=lambda track: track.get("ext") != "vtt"
            )

            subtitle_url = tracks[0].get("url")

            if subtitle_url:

                try:
                    print(
                        "AUSGEWÄHLTE UNTERTITEL:",
                        language
                    )

                    subtitle_text = download_subtitle_text(
                        subtitle_url
                    )

                    transcript = clean_subtitle_text(
                        subtitle_text
                    )

                    if transcript.strip():
                        print(
                            "QUIZLY: Untertitel erfolgreich geladen."
                        )

                        return transcript

                except requests.RequestException as error:

                    print(
                        "QUIZLY: Untertitel-Download fehlgeschlagen:",
                        error
                    )

                except Exception as error:

                    print(
                        "QUIZLY: Fehler bei Untertiteln:",
                        error
                    )

    # Keine brauchbaren Untertitel:
    # Audio herunterladen und mit Whisper transkribieren
    return get_transcript_from_audio(url)
