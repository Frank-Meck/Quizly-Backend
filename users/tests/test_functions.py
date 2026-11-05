
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework_simplejwt.tokens import RefreshToken

from users.functions import (
    validate_registration_data,
    create_registered_user,
    authenticate_user,
    create_auth_tokens,
)


User = get_user_model()


class ValidateRegistrationDataTests(TestCase):

    def setUp(self):
        self.data = {
            "username": "quiz_user",
            "email": "quiz@example.com",
            "password": "StrongPass123!",
            "confirmed_password": "StrongPass123!",
        }

    def test_valid_registration_data(self):
        self.assertIsNone(validate_registration_data(self.data))

    def test_missing_required_field(self):
        for field in self.data:
            data = self.data.copy()
            data[field] = ""

            with self.subTest(field=field):
                self.assertEqual(
                    validate_registration_data(data),
                    "All fields are required.",
                )

    def test_passwords_do_not_match(self):
        data = self.data.copy()
        data["confirmed_password"] = "DifferentPassword123!"

        self.assertEqual(
            validate_registration_data(data),
            "Passwords do not match.",
        )

    def test_email_already_registered(self):
        User.objects.create_user(
            username="existing_user",
            email="quiz@example.com",
            password="StrongPass123!",
        )

        self.assertEqual(
            validate_registration_data(self.data),
            "Email is already registered.",
        )

    def test_email_check_is_case_insensitive(self):
        User.objects.create_user(
            username="existing_user",
            email="QUIZ@EXAMPLE.COM",
            password="StrongPass123!",
        )

        self.assertEqual(
            validate_registration_data(self.data),
            "Email is already registered.",
        )

    def test_username_already_taken(self):
        User.objects.create_user(
            username="quiz_user",
            email="other@example.com",
            password="StrongPass123!",
        )

        self.assertEqual(
            validate_registration_data(self.data),
            "Username is already taken.",
        )


class CreateRegisteredUserTests(TestCase):

    def test_creates_user_with_correct_data(self):
        data = {
            "username": "quiz_user",
            "email": "quiz@example.com",
            "password": "StrongPass123!",
        }

        user = create_registered_user(data)

        self.assertEqual(user.username, "quiz_user")
        self.assertEqual(user.email, "quiz@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))


class AuthenticateUserTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="quiz_user",
            email="quiz@example.com",
            password="StrongPass123!",
        )

    def test_authenticate_with_valid_credentials(self):
        user = authenticate_user(
            "quiz_user",
            "StrongPass123!",
        )

        self.assertEqual(user, self.user)

    def test_authenticate_with_invalid_password(self):
        user = authenticate_user(
            "quiz_user",
            "WrongPassword123!",
        )

        self.assertIsNone(user)

    def test_authenticate_with_unknown_username(self):
        user = authenticate_user(
            "unknown_user",
            "StrongPass123!",
        )

        self.assertIsNone(user)


class CreateAuthTokensTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="quiz_user",
            email="quiz@example.com",
            password="StrongPass123!",
        )


    def test_creates_access_and_refresh_tokens(self):
        tokens = create_auth_tokens(self.user)

        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

        refresh = RefreshToken(tokens["refresh"])

        self.assertEqual(
            refresh["user_id"],
            str(self.user.id),
        )

        access = refresh.access_token

        self.assertEqual(
            access["user_id"],
            str(self.user.id),
        )

        self.assertEqual(
            access["token_type"],
            "access",
        )


    def test_tokens_are_valid_jwt_strings(self):
        tokens = create_auth_tokens(self.user)

        self.assertIsInstance(tokens["access"], str)
        self.assertIsInstance(tokens["refresh"], str)
        self.assertTrue(tokens["access"])
        self.assertTrue(tokens["refresh"])
