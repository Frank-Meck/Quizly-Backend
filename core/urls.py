
"""Define URL routes for the Quizly API and Django admin."""

from django.contrib import admin
from django.urls import path

from quizzes.api.views import CreateQuizView, GetQuizView
from users.views import (
    LoginView,
    LogoutView,
    RegisterView,
    TokenRefreshView,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/login/", LoginView.as_view(), name="login"),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/quizzes/",
        CreateQuizView.as_view(),
        name="create_quiz",
    ),
    path(
        "api/quizzes/<int:pk>/",
        GetQuizView.as_view(),
        name="get_quiz",
    ),
]
