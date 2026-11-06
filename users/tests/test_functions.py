from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework_simplejwt.tokens import RefreshToken

from users.functions import (
    authenticate_user,
    create_auth_tokens,
    create_registered_user,
    validate_registration_data,
)


User = get_user_model()


class ValidateRegistrationDataTests(TestCase):
    """Test registration data validation."""

    def setUp(self):
        """Prepare valid registration data."""
        self.data = {
            "username": "quiz_user",
            "email": "quiz@example.com",
            "password": "StrongPass123!",
            "confirmed_password": "StrongPass123!",
        }

    def test_valid_registration_data(self):
        """Accept valid registration data."""
        self.assertIsNone(validate_registration_data(self.data))

    def test_missing_required_field(self):
        """Reject registration data with missing fields."""
        for field in self.data:
            data = self.data.copy()
            data[field] = ""

            with self.subTest(field=field):
                self.assertEqual(
                    validate_registration_data(data),
                    "All fields are required.",
                )

    def test_passwords_do_not_match(self):
        """Reject registration data with different passwords."""
        data = self.data.copy()
        data["confirmed_password"] = "DifferentPassword123!"

        self.assertEqual(
            validate_registration_data(data),
            "Passwords do not match.",
        )

    def test_email_already_registered(self):
        """Reject an email address that is already registered."""
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
        """Reject an email address regardless of letter casing."""
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
        """Reject a username that is already registered."""
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
    """Test user creation."""

    def test_creates_user_with_correct_data(self):
        """Create a user and verify the stored credentials."""
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
    """Test user authentication."""

    def setUp(self):
        """Create a user for authentication tests."""
        self.user = User.objects.create_user(
            username="quiz_user",
            email="quiz@example.com",
            password="StrongPass123!",
        )

    def test_authenticate_with_valid_credentials(self):
        """Authenticate a user with valid credentials."""
        user = authenticate_user("quiz_user", "StrongPass123!")

        self.assertEqual(user, self.user)

    def test_authenticate_with_invalid_password(self):
        """Reject authentication with an incorrect password."""
        user = authenticate_user(
            "quiz_user",
            "WrongPassword123!",
        )

        self.assertIsNone(user)

    def test_authenticate_with_unknown_username(self):
        """Reject authentication for an unknown username."""
        user = authenticate_user(
            "unknown_user",
            "StrongPass123!",
        )

        self.assertIsNone(user)


class CreateAuthTokensTests(TestCase):
    """Test JWT access and refresh token creation."""

    def setUp(self):
        """Create a user for token generation tests."""
        self.user = User.objects.create_user(
            username="quiz_user",
            email="quiz@example.com",
            password="StrongPass123!",
        )

    def test_creates_access_and_refresh_tokens(self):
        """Generate valid tokens containing the user identifier."""
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
        self.assertEqual(access["token_type"], "access")

    def test_tokens_are_valid_jwt_strings(self):
        """Verify that both generated tokens are non-empty strings."""
        tokens = create_auth_tokens(self.user)

        self.assertIsInstance(tokens["access"], str)
        self.assertIsInstance(tokens["refresh"], str)
        self.assertTrue(tokens["access"])
        self.assertTrue(tokens["refresh"])