from django.db import models


class StoredFile(models.Model):
    name = models.CharField(max_length=500, unique=True)
    content = models.BinaryField()
    content_type = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "archivo"
        verbose_name_plural = "archivos"

    def __str__(self):
        return self.name
