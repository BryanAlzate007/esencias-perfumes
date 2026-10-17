from urllib.parse import urlsplit

from django.conf import settings


class DockerBrowserHostMiddleware:
    """The Compose proxy sends Host backend:8000. Google must receive the browser URL."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.META.get("HTTP_HOST", "")
        if settings.DEBUG and host.split(":")[0] == "backend":
            public = urlsplit(settings.FRONTEND_URL)
            if public.netloc:
                request.META["HTTP_HOST"] = public.netloc
        return self.get_response(request)
