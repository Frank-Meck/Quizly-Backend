
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase


User = get_user_model()


class RegisterTests(APITestCase):

    def test_register_creates_user(self):
        response = self.client.post(
            "/api/register/",
            {
                "username": "quiz_user",
                "email": "quiz@example.com",
                "password": "StrongPass123!",
                "confirmed_password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "detail": "User created successfully!"
            },
        )

    def test_register_rejects_missing_fields(self):
        response = self.client.post(
            "/api/register/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_register_rejects_password_mismatch(self):
        response = self.client.post(
            "/api/register/",
            {
                "username": "quiz_user",
                "email": "quiz@example.com",
                "password": "StrongPass123!",
                "confirmed_password": "DifferentPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existing_user",
            email="quiz@example.com",
            password="ExistingPass123!",
        )

        response = self.client.post(
            "/api/register/",
            {
                "username": "new_user",
                "email": "quiz@example.com",
                "password": "StrongPass123!",
                "confirmed_password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_register_rejects_duplicate_username(self):
        User.objects.create_user(
            username="existing_user",
            email="existing@example.com",
            password="ExistingPass123!",
        )

        response = self.client.post(
            "/api/register/",
            {
                "username": "existing_user",
                "email": "new@example.com",
                "password": "StrongPass123!",
                "confirmed_password": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "detail": "Username is already taken."
            },
        )
