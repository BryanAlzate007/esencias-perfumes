from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = Profile.Role.ADMIN if instance.is_staff else Profile.Role.CUSTOMER
        Profile.objects.get_or_create(user=instance, defaults={"role": role})
