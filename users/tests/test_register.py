
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_register_creates_user(api_client):
    response = api_client.post(
        "/api/register/",
        {
            "username": "quiz_user",
            "email": "quiz@example.com",
            "password": "StrongPass123!",
            "confirmed_password": "StrongPass123!",
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.json() == {
        "detail": "User created successfully!"
    }


@pytest.mark.django_db
def test_register_rejects_missing_fields(api_client):
    response = api_client.post(
        "/api/register/",
        {},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_register_rejects_password_mismatch(api_client):
    response = api_client.post(
        "/api/register/",
        {
            "username": "quiz_user",
            "email": "quiz@example.com",
            "password": "StrongPass123!",
            "confirmed_password": "DifferentPass123!",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_register_rejects_duplicate_email(api_client, django_user_model):
    django_user_model.objects.create_user(
        username="existing_user",
        email="quiz@example.com",
        password="ExistingPass123!",
    )

    response = api_client.post(
        "/api/register/",
        {
            "username": "new_user",
            "email": "quiz@example.com",
            "password": "StrongPass123!",
            "confirmed_password": "StrongPass123!",
        },
        format="json",
    )

    assert response.status_code == 400
