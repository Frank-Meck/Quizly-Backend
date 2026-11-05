from django.test import SimpleTestCase

from quizzes.models import Quiz, Question


class QuizModelTests(SimpleTestCase):

    def test_quiz_str_returns_title(self):
        quiz = Quiz(title="Python Grundlagen")

        self.assertEqual(
            str(quiz),
            "Python Grundlagen",
        )


class QuestionModelTests(SimpleTestCase):

    def test_question_str_returns_question_title(self):
        question = Question(
            question_title="Was ist Python?"
        )

        self.assertEqual(
            str(question),
            "Was ist Python?",
        )