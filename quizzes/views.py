from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from urllib.parse import urlparse

class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url = request.data.get("url")

        if not url:
            return Response(
                {"error": "A YouTube URL is required."},
                status=400,
            )

        try:
            URLValidator()(url)
        except ValidationError:
            return Response(
                {"error": "A valid URL is required."},
                status=400,
            )

        if not self.is_youtube_url(url):
            return Response(
                {"error": "A YouTube URL is required."},
                status=400,
            )
        return Response(status=501)

    def is_youtube_url(self, url):
        hostname = urlparse(url).hostname or ""
        allowed_domains = {"youtube.com", "www.youtube.com", "youtu.be"}

        return hostname.lower() in allowed_domains