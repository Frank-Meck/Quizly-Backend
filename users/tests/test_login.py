
from django.contrib.auth import get_user_model
from django.test import override_settings

from rest_framework.test import APITestCase


User = get_user_model()


class LoginTests(APITestCase):

    @override_settings(DEBUG=True)
    def test_login_returns_user_and_sets_auth_cookies(self):
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

        self.assertTrue(
            response.cookies["access_token"]["httponly"]
        )
        self.assertTrue(
            response.cookies["refresh_token"]["httponly"]
        )

        self.assertEqual(
            response.cookies["access_token"]["samesite"],
            "Lax",
        )
        self.assertEqual(
            response.cookies["refresh_token"]["samesite"],
            "Lax",
        )

        self.assertFalse(
            response.cookies["access_token"]["secure"]
        )
        self.assertFalse(
            response.cookies["refresh_token"]["secure"]
        )

    def test_login_rejects_missing_fields(self):
        response = self.client.post(
            "/api/login/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_login_rejects_invalid_credentials(self):
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
            {
                "detail": "Invalid username or password."
            },
        )

    def test_login_rejects_unknown_username(self):
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
            {
                "detail": "Invalid username or password."
            },
        )

    @override_settings(DEBUG=False)
    def test_login_sets_secure_auth_cookies(self):
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
        self.assertTrue(
            response.cookies["access_token"]["secure"]
        )
        self.assertTrue(
            response.cookies["refresh_token"]["secure"]
        )
