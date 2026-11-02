
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from users.serializers import RegisterSerializer


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
                "username": ["Username is already taken."]
            },
        )

class RegisterSerializerTests(APITestCase):

    def test_register_serializer_accepts_valid_data(self):
        serializer = RegisterSerializer(
            data={
                "username": "quiz_user",
                "email": "quiz@example.com",
                "password": "StrongPass123!",
                "confirmed_password": "StrongPass123!",
            }
        )

        self.assertTrue(serializer.is_valid())


    def test_register_serializer_rejects_password_mismatch(self):
        serializer = RegisterSerializer(
            data={
                "username": "quiz_user",
                "email": "quiz@example.com",
                "password": "StrongPass123!",
                "confirmed_password": "DifferentPass123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("confirmed_password", serializer.errors)

    def test_register_serializer_rejects_duplicate_email(self):
        User.objects.create_user(
            username="existing_user",
            email="quiz@example.com",
            password="ExistingPass123!",
        )

        serializer = RegisterSerializer(
            data={
                "username": "new_user",
                "email": "quiz@example.com",
                "password": "StrongPass123!",
                "confirmed_password": "StrongPass123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_register_serializer_rejects_duplicate_username(self):
        User.objects.create_user(
            username="existing_user",
            email="existing@example.com",
            password="ExistingPass123!",
        )

        serializer = RegisterSerializer(
            data={
                "username": "existing_user",
                "email": "new@example.com",
                "password": "StrongPass123!",
                "confirmed_password": "StrongPass123!",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_register_serializer_creates_user(self):
        serializer = RegisterSerializer(
            data={
                "username": "new_quiz_user",
                "email": "new_quiz@example.com",
                "password": "StrongPass123!",
                "confirmed_password": "StrongPass123!",
            }
        )

        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.username, "new_quiz_user")
        self.assertEqual(user.email, "new_quiz@example.com")
        self.assertTrue(
            user.check_password("StrongPass123!")
        )

    def test_register_serializer_password_is_write_only(self):
        serializer = RegisterSerializer()

        self.assertTrue(
            serializer.fields["password"].write_only
        )