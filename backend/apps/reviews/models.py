from django.conf import settings
from django.db import models

from apps.perfumes.models import Perfume


class Sentiment(models.TextChoices):
    LOVE = "love", "Encanta"
    LIKE = "like", "Me gusta"
    NEUTRAL = "neutral", "Me es indiferente"
    DISLIKE = "dislike", "No me gusta"
    HATE = "hate", "Lo odio"


class Occasion(models.TextChoices):
    WINTER = "winter", "Invierno"
    SPRING = "spring", "Primavera"
    SUMMER = "summer", "Verano"
    AUTUMN = "autumn", "Otoño"
    DAY = "day", "Día"
    NIGHT = "night", "Noche"


class Review(models.Model):
    perfume = models.ForeignKey(Perfume, related_name="reviews", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="reviews", on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.user} on {self.perfume}"


class Rating(models.Model):
    perfume = models.ForeignKey(Perfume, related_name="ratings", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ratings", on_delete=models.CASCADE)
    sentiment = models.CharField(max_length=20, choices=Sentiment.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("perfume", "user")

    def __str__(self):
        return f"{self.user} -> {self.perfume}: {self.sentiment}"


class OccasionVote(models.Model):
    perfume = models.ForeignKey(Perfume, related_name="occasion_votes", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="occasion_votes", on_delete=models.CASCADE)
    occasion = models.CharField(max_length=20, choices=Occasion.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("perfume", "user", "occasion")

    def __str__(self):
        return f"{self.user} -> {self.perfume}: {self.occasion}"
