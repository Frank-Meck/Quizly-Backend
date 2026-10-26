
from django.conf import settings

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.functions import (
    authenticate_user,
    create_auth_tokens,
    create_registered_user,
    validate_registration_data,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        error = validate_registration_data(request.data)

        if error:
            return Response(
                {"detail": error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        create_registered_user(request.data)

        return Response(
            {"detail": "User created successfully!"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate_user(username, password)

        if user is None:
            return Response(
                {"detail": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

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
        )

        response.set_cookie(
            "refresh_token",
            tokens["refresh"],
            httponly=True,
            secure=secure_cookie,
            samesite="Lax",
        )

        return response
