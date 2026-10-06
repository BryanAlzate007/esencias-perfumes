import mimetypes

from django.conf import settings
from django.http import HttpResponse
from django.views.static import serve

from apps.core.models import StoredFile


def stored_media(request, path):
    stored = StoredFile.objects.filter(name=path).first()
    if stored is not None:
        content_type = stored.content_type or mimetypes.guess_type(path)[0] or "application/octet-stream"
        response = HttpResponse(bytes(stored.content), content_type=content_type)
        response["Cache-Control"] = "public, max-age=86400"
        return response
    return serve(request, path, document_root=settings.MEDIA_ROOT)
