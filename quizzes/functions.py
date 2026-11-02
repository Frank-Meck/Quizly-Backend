import re

import yt_dlp
from google import genai


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
        raise ValueError("Quiz data must contain exactly ten questions.")


    question_titles = [
        question.get("question_title")
        for question in questions
        if isinstance(question, dict)
    ]

    if len(question_titles) != len(set(question_titles)):
        raise ValueError("Quiz questions must be unique.")


    for question in questions:
        if not isinstance(question, dict):
            raise ValueError("Each question must be a dictionary.")

        if not isinstance(question.get("question_title"), str):
            raise ValueError("Each question must have a title.")

        if not question["question_title"].strip():
            raise ValueError("Each question must have a title.")

        options = question.get("question_options")
        if not isinstance(options, list) or len(options) != 4:
            raise ValueError("Each question must have four options.")

        if not all(
            isinstance(option, str) and option.strip()
            for option in options
        ):
            raise ValueError("All question options must be non-empty strings.")

        if len(set(options)) != 4:
            raise ValueError("Question options must be unique.")

        answer = question.get("answer")
        if answer not in options:
            raise ValueError("The answer must be one of the options.")


def clean_gemini_response(response):
    response = response.strip()

    if response.startswith("```"):
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
    import json
    import os

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
- Generate the entire quiz in the same language as the transcript, including the title, description, questions, and answer options.
- Create a concise and relevant quiz title based on the transcript.
- Generate 3 easy questions.
- Generate 4 medium questions.
- Generate 3 difficult questions.
- Each question must have exactly 4 distinct options.
- Only one correct answer per question.
- Write clear and unambiguous questions.
- Use simple, natural, and easy-to-understand language.
- The answer must be one of the four options.
- Create plausible but incorrect answer options based on the transcript.
- Use only information explicitly stated in the transcript.
- Do not introduce external knowledge or invent facts.
- Cover different aspects of the transcript instead of repeating the same topic.
- Do not ask the same thing in different words.
- Return valid JSON only, without explanations or Markdown.

Transcript:
{transcript}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
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
    import requests

    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.text


def clean_subtitle_text(subtitle_text):
    lines = subtitle_text.splitlines()
    text_lines = [
        line.strip()
        for line in lines
        if line.strip()
        and line.strip() != "WEBVTT"
        and not re.match(
            r"^\d{2}:\d{2}:\d{2}\.\d{3}\s+-->",
            line.strip(),
        )
        and not re.fullmatch(r"\d+", line.strip())
    ]
    return " ".join(text_lines)


def get_youtube_transcript(url):

    options = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en", "de"],
        "subtitlesformat": "vtt",
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(options) as youtube_dl:
        info = youtube_dl.extract_info(url, download=False)

    subtitles = info.get("subtitles", {})
    automatic_captions = info.get("automatic_captions", {})
    available_subtitles = subtitles or automatic_captions

    if not available_subtitles:
        raise ValueError("No subtitles are available for this video.")

    language_subtitles = next(iter(available_subtitles.values()))
    subtitle_url = language_subtitles[0]["url"]
    return clean_subtitle_text(download_subtitle_text(subtitle_url))
