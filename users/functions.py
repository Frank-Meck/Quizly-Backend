from django.contrib.auth import authenticate, get_user_model

from rest_framework_simplejwt.tokens import RefreshToken


def validate_registration_data(data):
    """Validate required registration fields and uniqueness."""
    required_fields = (
        "username",
        "email",
        "password",
        "confirmed_password",
    )
    if not all(data.get(field) for field in required_fields):
        return "All fields are required."
    if data["password"] != data["confirmed_password"]:
        return "Passwords do not match."
    if validate_unique_email(data["email"]):
        return "Email is already registered."
    if validate_unique_username(data["username"]):
        return "Username is already taken."
    return None


def validate_unique_email(email):
    """Check whether an email address is already registered."""
    user_model = get_user_model()
    return user_model.objects.filter(email__iexact=email).exists()


def validate_unique_username(username):
    """Check whether a username is already registered."""
    user_model = get_user_model()
    return user_model.objects.filter(username=username).exists()


def create_registered_user(data):
    """Create a user with a securely hashed password."""
    user_model = get_user_model()
    return user_model.objects.create_user(**data)


def authenticate_user(username, password):
    """Authenticate a user with their username and password."""
    return authenticate(username=username, password=password)


def create_auth_tokens(user):
    """Generate access and refresh tokens for an authenticated user."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }