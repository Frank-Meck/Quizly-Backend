
from django.contrib.auth import get_user_model


def validate_registration_data(data):
    required_fields = [
        "username",
        "email",
        "password",
        "confirmed_password",
    ]

    if not all(data.get(field) for field in required_fields):
        return "All fields are required."
    if data["password"] != data["confirmed_password"]:
        return "Passwords do not match."

    user_model = get_user_model()
    if user_model.objects.filter(email__iexact=data["email"]).exists():
        return "Email is already registered."
    if user_model.objects.filter(username=data["username"]).exists():
        return "Username is already taken."

    return None


def create_registered_user(data):
    user_model = get_user_model()
    return user_model.objects.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"],
    )



def authenticate_user(username, password):
    from django.contrib.auth import authenticate

    return authenticate(username=username, password=password)


def create_auth_tokens(user):
    from rest_framework_simplejwt.tokens import RefreshToken

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
