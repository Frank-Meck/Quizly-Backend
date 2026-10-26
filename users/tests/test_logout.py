from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken


User = get_user_model()


class LogoutTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

    def test_logout_without_authentication_returns_401(self):
        response = self.client.post("/api/logout/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_successful_logout_blacklists_refresh_token_and_deletes_cookies(self):
        self.client.cookies["access_token"] = self.access_token
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post("/api/logout/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token__jti=self.refresh["jti"],
            ).exists()
        )

        for cookie_name in ("access_token", "refresh_token"):
            self.assertEqual(response.cookies[cookie_name].value, "")
            self.assertEqual(response.cookies[cookie_name]["max-age"], 0)

    def test_logout_with_invalid_refresh_token_returns_401(self):
        self.client.cookies["access_token"] = self.access_token
        self.client.cookies["refresh_token"] = "invalid-refresh-token"

        response = self.client.post("/api/logout/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
