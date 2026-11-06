
"""Test validation of generated quiz data."""

from django.test import SimpleTestCase

from quizzes.functions import validate_quiz_data


def _build_valid_quiz_data():
    """Build valid quiz data containing ten questions."""
    return {
        "title": "Python Basics",
        "description": "An introduction to Python.",
        "questions": [
            {
                "question_title": f"Question {number}",
                "question_options": [
                    "Option A",
                    "Option B",
                    "Option C",
                    "Option D",
                ],
                "answer": "Option A",
            }
            for number in range(1, 11)
        ],
    }


class ValidateQuizDataTests(SimpleTestCase):
    """Test validation of quiz data and individual questions."""

    def test_rejects_question_with_fewer_than_four_options(self):
        """Reject questions containing fewer than four options."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"][0]["question_options"] = [
            "Option A",
            "Option B",
            "Option C",
        ]

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_answer_not_in_question_options(self):
        """Reject answers that are not included in the options."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"][0]["answer"] = "Invalid Answer"

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_quiz_with_fewer_than_ten_questions(self):
        """Reject quizzes containing fewer than ten questions."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"].pop()

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_question_without_title(self):
        """Reject questions without a title."""
        quiz_data = _build_valid_quiz_data()
        del quiz_data["questions"][0]["question_title"]

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_quiz_without_title(self):
        """Reject quiz data without a title."""
        quiz_data = _build_valid_quiz_data()
        del quiz_data["title"]

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_quiz_without_description(self):
        """Reject quiz data without a description."""
        quiz_data = _build_valid_quiz_data()
        del quiz_data["description"]

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_question_that_is_not_a_dictionary(self):
        """Reject questions that are not dictionaries."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"][0] = "Invalid question"

        with self.assertRaisesRegex(
            ValueError,
            "Each question must be a dictionary.",
        ):
            validate_quiz_data(quiz_data)

    def test_rejects_duplicate_question_options(self):
        """Reject questions containing duplicate answer options."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"][0]["question_options"] = [
            "Option A",
            "Option A",
            "Option C",
            "Option D",
        ]

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_non_string_question_options(self):
        """Reject answer options that are not strings."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"][0]["question_options"][3] = 123

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_description_longer_than_150_characters(self):
        """Reject descriptions exceeding 150 characters."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["description"] = "A" * 151

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_accepts_description_with_exactly_150_characters(self):
        """Accept descriptions containing exactly 150 characters."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["description"] = "A" * 150

        try:
            validate_quiz_data(quiz_data)
        except ValueError:
            self.fail("A 150-character description should be valid.")

    def test_rejects_duplicate_questions(self):
        """Reject quizzes containing duplicate question titles."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"][1]["question_title"] = (
            quiz_data["questions"][0]["question_title"]
        )

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_empty_description(self):
        """Reject descriptions containing only whitespace."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["description"] = "   "

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_question_title_that_is_not_a_string(self):
        """Reject question titles that are not strings."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"][0]["question_title"] = [
            "Invalid",
            "Title",
        ]

        with self.assertRaisesRegex(
            ValueError,
            "Each question must have a title.",
        ):
            validate_quiz_data(quiz_data)

    def test_rejects_missing_questions(self):
        """Reject quiz data without a questions field."""
        quiz_data = {
            "title": "Test Quiz",
            "description": "A test description.",
        }

        with self.assertRaisesRegex(
            ValueError,
            "Quiz data must contain exactly ten questions.",
        ):
            validate_quiz_data(quiz_data)

    def test_rejects_questions_that_are_not_a_list(self):
        """Reject questions when the field is not a list."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"] = "Invalid questions"

        with self.assertRaisesRegex(
            ValueError,
            "Quiz data must contain exactly ten questions.",
        ):
            validate_quiz_data(quiz_data)

    def test_rejects_non_dictionary_quiz_data(self):
        """Reject quiz data that is not a dictionary."""
        with self.assertRaisesRegex(
            ValueError,
            "Quiz data must be a dictionary.",
        ):
            validate_quiz_data("not a dictionary")

    def test_rejects_option_containing_only_whitespace(self):
        """Reject answer options containing only whitespace."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"][0]["question_options"][0] = "   "

        with self.assertRaisesRegex(
            ValueError,
            "All question options must be non-empty strings.",
        ):
            validate_quiz_data(quiz_data)

    def test_rejects_missing_answer(self):
        """Reject questions without a valid answer."""
        quiz_data = _build_valid_quiz_data()
        del quiz_data["questions"][0]["answer"]

        with self.assertRaisesRegex(
            ValueError,
            "The answer must be one of the options.",
        ):
            validate_quiz_data(quiz_data)

    def test_rejects_question_with_wrong_number_of_options(self):
        """Reject questions that do not contain exactly four options."""
        quiz_data = _build_valid_quiz_data()
        quiz_data["questions"][0]["question_options"] = [
            "Option A",
            "Option B",
            "Option C",
            "Option D",
            "Option E",
        ]

        with self.assertRaisesRegex(
            ValueError,
            "Each question must have four options.",
        ):
            validate_quiz_data(quiz_data)
