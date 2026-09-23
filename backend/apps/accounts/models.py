from django.conf import settings
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        ADMIN = "admin", "Admin"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    country = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    profile_person = models.ForeignKey('Profile_person', on_delete=models.CASCADE, related_name='profiles', null=True, blank=True)
    preferred_language = models.CharField(max_length=8, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"



class Profile_person(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  class Meta:
    ordering = ["name"]

  def __str__(self):
    return self.name