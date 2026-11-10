
"""Validate generated quiz data."""


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

    normalized_title = question_title.strip()

    if normalized_title in question_titles:
        raise ValueError("Quiz questions must be unique.")

    question_titles.add(normalized_title)

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

    if len({option.strip() for option in options}) != 4:
        raise ValueError("Question options must be unique.")

    if question.get("answer") not in options:
        raise ValueError("The answer must be one of the options.")
