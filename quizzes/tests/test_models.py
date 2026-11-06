
"""Test the string representations of quiz models."""

from django.test import SimpleTestCase

from quizzes.models import Question, Quiz


class QuizModelTests(SimpleTestCase):
    """Test the Quiz model."""

    def test_quiz_str_returns_title(self):
        """Return the quiz title as its string representation."""
        quiz = Quiz(title="Python Grundlagen")

        self.assertEqual(str(quiz), "Python Grundlagen")


class QuestionModelTests(SimpleTestCase):
    """Test the Question model."""

    def test_question_str_returns_question_title(self):
        """Return the question title as its string representation."""
        question = Question(question_title="Was ist Python?")

        self.assertEqual(str(question), "Was ist Python?")
