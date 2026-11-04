
from django.conf import settings

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from users.functions import create_auth_tokens
from users.serializers import (
    LoginSerializer,
    LogoutSerializer,
    RegisterSerializer,
    TokenRefreshSerializer,
)


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "User created successfully!"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
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

        response.set_cookie(
            "access_token",
            tokens["access"],
            httponly=True,
            secure=secure_cookie,
            samesite="Lax",
            path="/",
        )

        response.set_cookie(
            "refresh_token",
            tokens["refresh"],
            httponly=True,
            secure=secure_cookie,
            samesite="Lax",
            path="/",
        )

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = LogoutSerializer(
            data={"refresh_token": refresh_token}
        )

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
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

        secure_cookie = not settings.DEBUG

        for cookie_name in ("access_token", "refresh_token"):
            response.set_cookie(
                cookie_name,
                "",
                max_age=0,
                httponly=True,
                secure=secure_cookie,
                samesite="Lax",
                path="/",
            )

        return response


class TokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
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
