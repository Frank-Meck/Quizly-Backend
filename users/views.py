
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.functions import (
    create_registered_user,
    validate_registration_data,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
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
