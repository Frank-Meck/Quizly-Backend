
from datetime import timedelta

from django.contrib.auth import get_user_model

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


User = get_user_model()


class TokenRefreshTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="refreshuser",
            email="refresh@example.com",
            password="TestPassword123!",
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)

    def test_refresh_with_valid_cookie_returns_new_access_cookie(self):
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post("/api/token/refresh/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "Token refreshed"})
        self.assertIn("access_token", response.cookies)
        self.assertTrue(response.cookies["access_token"]["httponly"])

    def test_refresh_without_cookie_returns_401(self):
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_with_invalid_token_returns_401(self):
        self.client.cookies["refresh_token"] = "invalid-refresh-token"

        response = self.client.post("/api/token/refresh/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_refresh_with_expired_token_returns_401(self):
        refresh = RefreshToken.for_user(self.user)
        refresh.set_exp(
            from_time=timezone.now() - timedelta(days=1),
            lifetime=timedelta(seconds=0),
        )
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.post("/api/token/refresh/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


    def test_refresh_with_blacklisted_token_returns_401(self):
        self.refresh.blacklist()
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post("/api/token/refresh/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

