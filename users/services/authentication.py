from django.contrib.auth import authenticate


def authenticate_user(username, password):
    """Authenticate a user with their username and password."""
    return authenticate(username=username, password=password)