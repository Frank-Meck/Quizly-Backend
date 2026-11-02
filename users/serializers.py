from django.contrib.auth import authenticate, get_user_model

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
    )
    confirmed_password = serializers.CharField()

    def validate(self, data):
        if data["password"] != data["confirmed_password"]:
            raise serializers.ValidationError(
                {
                    "confirmed_password": "Passwords do not match."
                }
            )

        return data

    def validate_email(self, value):
        user_model = get_user_model()

        if user_model.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Email is already registered."
            )

        return value

    def validate_username(self, value):
        user_model = get_user_model()

        if user_model.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Username is already taken."
            )

        return value

    def create(self, validated_data):
        validated_data.pop("confirmed_password")

        user_model = get_user_model()

        return user_model.objects.create_user(
            **validated_data
        )


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
    )

    def validate(self, data):
        user = authenticate(
            username=data["username"],
            password=data["password"],
        )

        if user is None:
            raise AuthenticationFailed(
                "Invalid username or password."
            )

        data["user"] = user
        return data


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        write_only=True,
    )

    def validate_refresh_token(self, value):
        try:
            token = RefreshToken(value)
        except TokenError:
            raise serializers.ValidationError(
                "Refresh token is invalid."
            )

        return token

    def save(self, **kwargs):
        token = self.validated_data["refresh_token"]
        token.blacklist()

        return token


class TokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(
        write_only=True,
    )

    def validate_refresh_token(self, value):
        try:
            return RefreshToken(value)
        except TokenError:
            raise serializers.ValidationError(
                "Refresh token is invalid."
            )

    def validate(self, data):
        token = data["refresh_token"]

        return {
            "access_token": str(token.access_token),
        }