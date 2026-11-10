
from django.conf import settings

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.api.serializers import (
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    TokenRefreshSerializer,
)
from users.services.tokens import create_auth_tokens


class RegisterView(APIView):
    """Handle user registration requests."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Validate registration data and create a new user."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "User created successfully!"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Handle user login and JWT cookie creation."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate the user and set JWT cookies."""
        serializer = LoginSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except AuthenticationFailed:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = serializer.validated_data["user"]
        tokens = create_auth_tokens(user)

        response = Response(
            {
                "detail": "Login successfully!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )

        secure_cookie = not settings.DEBUG
        cookie_options = {
            "httponly": True,
            "secure": secure_cookie,
            "samesite": "Lax",
            "path": "/",
        }

        response.set_cookie(
            "access_token",
            tokens["access"],
            **cookie_options,
        )
        response.set_cookie(
            "refresh_token",
            tokens["refresh"],
            **cookie_options,
        )

        return response


class LogoutView(APIView):
    """Handle user logout and refresh token invalidation."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Blacklist the refresh token and clear authentication cookies."""
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = LogoutSerializer(
            data={"refresh_token": refresh_token}
        )

        if not serializer.is_valid():
            return Response(
                {"detail": "Refresh token is invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer.save()

        response = Response(
            {
                "detail": (
                    "Log-Out successfully! All Tokens will be deleted. "
                    "Refresh token is now invalid."
                )
            },
            status=status.HTTP_200_OK,
        )

        cookie_options = {
            "max_age": 0,
            "httponly": True,
            "secure": not settings.DEBUG,
            "samesite": "Lax",
            "path": "/",
        }

        for cookie_name in ("access_token", "refresh_token"):
            response.set_cookie(cookie_name, "", **cookie_options)

        return response


class TokenRefreshView(APIView):
    """Handle access token renewal using refresh cookies."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Validate the refresh token and issue a new access cookie."""
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = TokenRefreshSerializer(
            data={"refresh_token": refresh_token}
        )

        if not serializer.is_valid():
            return Response(
                {"detail": "Refresh token is invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            {"detail": "Token refreshed"},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            "access_token",
            serializer.validated_data["access_token"],
            httponly=True,
            secure=not settings.DEBUG,
            samesite="Lax",
            path="/",
        )

        return response
