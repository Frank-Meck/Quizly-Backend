
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.api.serializers import TokenRefreshSerializer


User = get_user_model()


class TokenRefreshTests(APITestCase):
    """Test the token refresh API."""

    def setUp(self):
        """Create a user and generate a refresh token."""
        self.user = User.objects.create_user(
            username="refreshuser",
            email="refresh@example.com",
            password="TestPassword123!",
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)

    def test_refresh_with_valid_cookie_returns_new_access_cookie(self):
        """Issue a new access token for a valid refresh cookie."""
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post("/api/token/refresh/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"detail": "Token refreshed"})
        self.assertIn("access_token", response.cookies)
        self.assertTrue(response.cookies["access_token"]["httponly"])

    def test_refresh_without_cookie_returns_401(self):
        """Reject refresh requests without a refresh cookie."""
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_with_invalid_token_returns_401(self):
        """Reject refresh requests with an invalid token."""
        self.client.cookies["refresh_token"] = "invalid-refresh-token"

        response = self.client.post("/api/token/refresh/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_with_expired_token_returns_401(self):
        """Reject refresh requests with an expired token."""
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
        """Reject refresh requests with a blacklisted token."""
        self.refresh.blacklist()
        self.client.cookies["refresh_token"] = self.refresh_token

        response = self.client.post("/api/token/refresh/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class TokenRefreshSerializerTests(APITestCase):
    """Test the token refresh serializer."""

    def setUp(self):
        """Create a user and generate a refresh token."""
        self.user = User.objects.create_user(
            username="serializeruser",
            email="serializer@example.com",
            password="TestPassword123!",
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.refresh_token = str(self.refresh)

    def test_serializer_accepts_valid_refresh_token(self):
        """Accept a valid refresh token and return an access token."""
        serializer = TokenRefreshSerializer(
            data={"refresh_token": self.refresh_token}
        )

        self.assertTrue(serializer.is_valid())
        self.assertIn("access_token", serializer.validated_data)

    def test_serializer_rejects_invalid_refresh_token(self):
        """Reject an invalid refresh token."""
        serializer = TokenRefreshSerializer(
            data={"refresh_token": "invalid-refresh-token"}
        )

        self.assertFalse(serializer.is_valid())

    def test_serializer_rejects_expired_refresh_token(self):
        """Reject an expired refresh token."""
        self.refresh.set_exp(
            from_time=timezone.now() - timedelta(days=1),
            lifetime=timedelta(seconds=0),
        )
        serializer = TokenRefreshSerializer(
            data={"refresh_token": str(self.refresh)}
        )

        self.assertFalse(serializer.is_valid())

    def test_serializer_rejects_blacklisted_refresh_token(self):
        """Reject a blacklisted refresh token."""
        self.refresh.blacklist()
        serializer = TokenRefreshSerializer(
            data={"refresh_token": self.refresh_token}
        )

        self.assertFalse(serializer.is_valid())
