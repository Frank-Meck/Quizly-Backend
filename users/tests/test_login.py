from django.contrib.auth import get_user_model
from django.test import override_settings

from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APITestCase

from users.api.serializers import LoginSerializer


User = get_user_model()


class LoginTests(APITestCase):
    """Test the user login API."""

    @override_settings(DEBUG=True)
    def test_login_returns_user_and_sets_auth_cookies(self):
        """Authenticate a user and verify the authentication cookies."""
        user = User.objects.create_user(
            username="quiz_user",
            email="quiz@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/api/login/",
            {
                "username": "quiz_user",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "detail": "Login successfully!",
                "user": {
                    "id": user.id,
                    "username": "quiz_user",
                    "email": "quiz@example.com",
                },
            },
        )

        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

        for cookie_name in ("access_token", "refresh_token"):
            cookie = response.cookies[cookie_name]
            self.assertTrue(cookie["httponly"])
            self.assertEqual(cookie["samesite"], "Lax")
            self.assertFalse(cookie["secure"])

    def test_login_rejects_missing_fields(self):
        """Reject login requests with missing credentials."""
        response = self.client.post(
            "/api/login/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_login_rejects_invalid_credentials(self):
        """Reject login requests with an incorrect password."""
        User.objects.create_user(
            username="quiz_user",
            email="quiz@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/api/login/",
            {
                "username": "quiz_user",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"detail": "Invalid username or password."},
        )

    def test_login_rejects_unknown_username(self):
        """Reject login requests for unknown usernames."""
        response = self.client.post(
            "/api/login/",
            {
                "username": "unknown_user",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"detail": "Invalid username or password."},
        )

    @override_settings(DEBUG=False)
    def test_login_sets_secure_auth_cookies(self):
        """Ensure authentication cookies are secure in production."""
        User.objects.create_user(
            username="secure_user",
            email="secure@example.com",
            password="StrongPass123!",
        )

        response = self.client.post(
            "/api/login/",
            {
                "username": "secure_user",
                "password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        for cookie_name in ("access_token", "refresh_token"):
            self.assertTrue(response.cookies[cookie_name]["secure"])


class LoginSerializerTests(APITestCase):
    """Test the login serializer."""

    def test_login_serializer_accepts_valid_credentials(self):
        """Accept valid username and password combinations."""
        User.objects.create_user(
            username="quiz_user",
            email="quiz@example.com",
            password="StrongPass123!",
        )

        serializer = LoginSerializer(
            data={
                "username": "quiz_user",
                "password": "StrongPass123!",
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_login_serializer_rejects_invalid_credentials(self):
        """Raise an authentication error for invalid credentials."""
        User.objects.create_user(
            username="quiz_user",
            email="quiz@example.com",
            password="StrongPass123!",
        )

        serializer = LoginSerializer(
            data={
                "username": "quiz_user",
                "password": "WrongPassword123!",
            }
        )

        with self.assertRaises(AuthenticationFailed):
            serializer.is_valid()
