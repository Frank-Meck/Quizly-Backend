
from django.contrib import admin
from django.urls import path

from users.views import register


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/register/", register, name="register"),
]
