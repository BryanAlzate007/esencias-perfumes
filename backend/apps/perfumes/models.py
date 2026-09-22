from django.db import models


class Perfume(models.Model):
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=120)
    description = models.TextField()
    notes = models.CharField(max_length=200, blank=True)
    image_url = models.URLField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.brand} {self.name}"
