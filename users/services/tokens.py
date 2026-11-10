from rest_framework_simplejwt.tokens import RefreshToken


def create_auth_tokens(user):
    """Generate access and refresh tokens for an authenticated user."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }