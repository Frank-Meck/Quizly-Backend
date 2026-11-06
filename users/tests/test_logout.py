
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

from users.serializers import LogoutSerializer


User = get_user_model()


class LogoutTests(APITestCase):
    """Test the user logout API."""

    def setUp(self):
        """Create a user and generate authentication tokens."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="TestPassword123!",
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

    def test_logout_without_authentication_returns_401(self):
        """Reject logout requests without authentication."""
        response = self.client.post("/api/logout/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_without_refresh_token_returns_401(self):
        """Reject logout requests without a refresh token."""
        self.client.cookies["access_token"] = self.access_token

        response = self.client.post("/api/logout/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            response.data["detail"],
            "Refresh token is missing.",
        )

    def test_successful_logout_blacklists_refresh_token_and_deletes_cookies(
        self,
    ):
        """Blacklist the refresh token and clear authentication cookies."""
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
            cookie = response.cookies[cookie_name]
            self.assertEqual(cookie.value, "")
            self.assertEqual(cookie["max-age"], 0)

    def test_logout_with_invalid_refresh_token_returns_401(self):
        """Reject logout requests with an invalid refresh token."""
        self.client.cookies["access_token"] = self.access_token
        self.client.cookies["refresh_token"] = "invalid-refresh-token"

        response = self.client.post("/api/logout/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class LogoutSerializerTests(APITestCase):
    """Test the logout serializer."""

    def test_logout_serializer_accepts_valid_refresh_token(self):
        """Accept a valid refresh token."""
        user = User.objects.create_user(
            username="logout_user",
            email="logout@example.com",
            password="StrongPass123!",
        )

        refresh_token = str(RefreshToken.for_user(user))

        serializer = LogoutSerializer(
            data={"refresh_token": refresh_token}
        )

        self.assertTrue(serializer.is_valid())

    def test_logout_serializer_rejects_invalid_refresh_token(self):
        """Reject an invalid refresh token."""
        serializer = LogoutSerializer(
            data={"refresh_token": "invalid-refresh-token"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("refresh_token", serializer.errors)
