from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from users.services.authentication import authenticate_user
from users.services.registration import (
    create_registered_user,
    validate_unique_email,
    validate_unique_username,
)


class RegisterSerializer(serializers.Serializer):
    """Validate registration data and create new users."""

    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )
    confirmed_password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, data):
        """Check whether both password fields match."""
        if data["password"] != data["confirmed_password"]:
            raise serializers.ValidationError(
                {"confirmed_password": "Passwords do not match."}
            )
        return data

    def validate_email(self, value):
        """Check whether the email address is available."""
        if validate_unique_email(value):
            raise serializers.ValidationError(
                "Email is already registered."
            )
        return value

    def validate_username(self, value):
        """Check whether the username is available."""
        if validate_unique_username(value):
            raise serializers.ValidationError(
                "Username is already taken."
            )
        return value

    def create(self, validated_data):
        """Create a user after removing the confirmation field."""
        validated_data.pop("confirmed_password")
        return create_registered_user(validated_data)


class LoginSerializer(serializers.Serializer):
    """Validate login credentials and retrieve the user."""

    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, data):
        """Authenticate the submitted username and password."""
        user = authenticate_user(
            data["username"],
            data["password"],
        )
        if user is None:
            raise AuthenticationFailed(
                "Invalid username or password."
            )
        data["user"] = user
        return data


class LogoutSerializer(serializers.Serializer):
    """Validate and blacklist a refresh token."""

    refresh_token = serializers.CharField(write_only=True)

    def validate_refresh_token(self, value):
        """Validate the submitted refresh token."""
        try:
            return RefreshToken(value)
        except TokenError as exc:
            raise serializers.ValidationError(
                "Refresh token is invalid."
            ) from exc

    def save(self, **kwargs):
        """Blacklist the validated refresh token."""
        token = self.validated_data["refresh_token"]
        token.blacklist()
        return token


class TokenRefreshSerializer(serializers.Serializer):
    """Validate a refresh token and generate a new access token."""

    refresh_token = serializers.CharField(write_only=True)

    def validate_refresh_token(self, value):
        """Validate the submitted refresh token."""
        try:
            return RefreshToken(value)
        except TokenError as exc:
            raise serializers.ValidationError(
                "Refresh token is invalid."
            ) from exc

    def validate(self, data):
        """Generate a new access token from the refresh token."""
        token = data["refresh_token"]
        return {"access_token": str(token.access_token)}