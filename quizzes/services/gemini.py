"""Generate quiz data using the Gemini API."""

import json
import logging
import os
import re
import time

from google import genai
from google.genai import errors


logger = logging.getLogger(__name__)


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