from django.test import SimpleTestCase
from quizzes.functions import validate_quiz_data


class ValidateQuizDataTests(SimpleTestCase):

    def test_rejects_question_with_fewer_than_four_options(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": ["Language", "Browser", "Database"],
                    "answer": "Language",
                }
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_answer_not_in_question_options(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": [
                        "Language",
                        "Browser",
                        "Database",
                        "Editor",
                    ],
                    "answer": "Operating system",
                }
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_quiz_with_fewer_than_ten_questions(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": "What is Python?",
                    "question_options": [
                        "Language",
                        "Browser",
                        "Database",
                        "Editor",
                    ],
                    "answer": "Language",
                }
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_question_without_title(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_options": [
                        "Language",
                        "Browser",
                        "Database",
                        "Editor",
                    ],
                    "answer": "Language",
                }
                for _ in range(10)
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_quiz_without_title(self):
        quiz_data = {
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

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_quiz_without_description(self):
        quiz_data = {
            "title": "Python Basics",
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

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_question_that_is_not_a_dictionary(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": ["Invalid question"] + [
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
                for number in range(2, 11)
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_duplicate_question_options(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": f"Question {number}",
                    "question_options": [
                        "Option A",
                        "Option A",
                        "Option C",
                        "Option D",
                    ],
                    "answer": "Option A",
                }
                for number in range(1, 11)
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)

    def test_rejects_non_string_question_options(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": f"Question {number}",
                    "question_options": [
                        "Option A",
                        "Option B",
                        "Option C",
                        123,
                    ],
                    "answer": "Option A",
                }
                for number in range(1, 11)
            ],
        }

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)


    def test_rejects_description_longer_than_150_characters(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "A" * 151,
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

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)



    def test_accepts_description_with_exactly_150_characters(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "A" * 150,
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

        try:
            validate_quiz_data(quiz_data)
        except ValueError:
            self.fail("A 150-character description should be valid.")



    def test_rejects_duplicate_questions(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": (
                        "What is Python?"
                        if number == 1
                        else f"What is question {number}?"
                    ),
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

        quiz_data["questions"][1]["question_title"] = (
            quiz_data["questions"][0]["question_title"]
        )

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)


    def test_rejects_empty_description(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "   ",
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

        with self.assertRaises(ValueError):
            validate_quiz_data(quiz_data)



    def test_validate_quiz_data_rejects_question_title_that_is_not_a_string(self):
        quiz_data = {
            "title": "Test Quiz",
            "description": "A test description.",
            "questions": [
                {
                    "question_title": f"Question {i}",
                    "question_options": [
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D"
                    ],
                    "answer": "Option A"
                }
                for i in range(10)
            ]
        }

        quiz_data["questions"][0]["question_title"] = ["Invalid", "Title"]

        with self.assertRaisesRegex(
            ValueError,
            "Each question must have a title."
        ):
            validate_quiz_data(quiz_data)



    def test_validate_quiz_data_rejects_answer_that_is_not_an_option(self):
        quiz_data = {
            "title": "Test Quiz",
            "description": "A test description.",
            "questions": [
                {
                    "question_title": f"Question {i}",
                    "question_options": [
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D"
                    ],
                    "answer": "Option A"
                }
                for i in range(10)
            ]
        }

        quiz_data["questions"][0]["answer"] = "Invalid Answer"

        with self.assertRaisesRegex(
            ValueError,
            "The answer must be one of the options."
        ):
            validate_quiz_data(quiz_data)



    def test_validate_quiz_data_rejects_missing_questions(self):
        quiz_data = {
            "title": "Test Quiz",
            "description": "A test description."
        }

        with self.assertRaisesRegex(
            ValueError,
            "Quiz data must contain exactly ten questions."
        ):
            validate_quiz_data(quiz_data)


    def test_validate_quiz_data_rejects_questions_that_are_not_a_list(self):
        quiz_data = {
            "title": "Test Quiz",
            "description": "A test description.",
            "questions": "Invalid questions"
        }

        with self.assertRaisesRegex(
            ValueError,
            "Quiz data must contain exactly ten questions."
        ):
            validate_quiz_data(quiz_data)


    def test_validate_quiz_data_rejects_question_that_is_not_a_dictionary(self):
        quiz_data = {
            "title": "Test Quiz",
            "description": "A test description.",
            "questions": [
                {
                    "question_title": f"Question {i}",
                    "question_options": [
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D"
                    ],
                    "answer": "Option A"
                }
                for i in range(10)
            ]
        }

        quiz_data["questions"][0] = "Invalid question"

        with self.assertRaisesRegex(
            ValueError,
            "Each question must be a dictionary."
        ):
            validate_quiz_data(quiz_data)


    def test_validate_quiz_data_rejects_option_containing_only_whitespace(self):
        quiz_data = {
            "title": "Test Quiz",
            "description": "A test description.",
            "questions": [
                {
                    "question_title": f"Question {i}",
                    "question_options": [
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D"
                    ],
                    "answer": "Option A"
                }
                for i in range(10)
            ]
        }

        quiz_data["questions"][0]["question_options"][0] = "   "

        with self.assertRaisesRegex(
            ValueError,
            "All question options must be non-empty strings."
        ):
            validate_quiz_data(quiz_data)


    def test_validate_quiz_data_rejects_missing_answer(self):
        quiz_data = {
            "title": "Test Quiz",
            "description": "A test description.",
            "questions": [
                {
                    "question_title": f"Question {i}",
                    "question_options": [
                        "Option A",
                        "Option B",
                        "Option C",
                        "Option D"
                    ],
                    "answer": "Option A"
                }
                for i in range(10)
            ]
        }

        del quiz_data["questions"][0]["answer"]

        with self.assertRaisesRegex(
            ValueError,
            "The answer must be one of the options."
        ):
            validate_quiz_data(quiz_data)


    def test_rejects_non_dictionary_quiz_data(self):
        with self.assertRaisesMessage(
            ValueError,
            "Quiz data must be a dictionary.",
        ):
            validate_quiz_data("not a dictionary")

    def test_rejects_question_with_wrong_number_of_options(self):
        quiz_data = {
            "title": "Python Basics",
            "description": "An introduction to Python.",
            "questions": [
                {
                    "question_title": f"Question {number}",
                    "question_options": (
                        ["Option A", "Option B", "Option C"]
                        if number == 1
                        else [
                            "Option A",
                            "Option B",
                            "Option C",
                            "Option D",
                        ]
                    ),
                    "answer": "Option A",
                }
                for number in range(1, 11)
            ],
        }

        with self.assertRaisesMessage(
            ValueError,
            "Each question must have four options.",
        ):
            validate_quiz_data(quiz_data)
