import mimetypes

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class DatabaseStorage(Storage):
    """Keeps uploads in Postgres so they survive Render's ephemeral disk."""

    def _open(self, name, mode="rb"):
        stored = self._model().objects.get(name=name)
        return ContentFile(bytes(stored.content))

    def _save(self, name, content):
        if hasattr(content, "seek"):
            content.seek(0)
        data = content.read()
        content_type = getattr(content, "content_type", "") or ""
        if not content_type:
            content_type = mimetypes.guess_type(name)[0] or "application/octet-stream"
        self._model().objects.update_or_create(
            name=name,
            defaults={"content": data, "content_type": content_type},
        )
        return name

    def delete(self, name):
        self._model().objects.filter(name=name).delete()

    def exists(self, name):
        return self._model().objects.filter(name=name).exists()

    def size(self, name):
        stored = self._model().objects.get(name=name)
        return len(stored.content)

    def url(self, name):
        base = settings.MEDIA_URL
        if not base.endswith("/"):
            base = f"{base}/"
        return f"{base}{name}"

    @staticmethod
    def _model():
        from apps.core.models import StoredFile

        return StoredFile
