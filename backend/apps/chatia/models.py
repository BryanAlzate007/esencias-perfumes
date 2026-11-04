import uuid

from django.conf import settings
from django.db import models


class ChatIA(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    advisor_name = models.CharField(max_length=80, blank=True)
    language = models.CharField(max_length=8, default="es")
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Cliente"
        ASSISTANT = "assistant", "Asesor"

    chatia = models.ForeignKey("ChatIA", on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return self.content


class OlfactoryTest(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "En curso"
        AWAITING_EMAIL = "awaiting_email", "Esperando correo"
        COMPLETED = "completed", "Completado"

    chat = models.OneToOneField(ChatIA, on_delete=models.CASCADE, related_name="olfactory_test")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="olfactory_tests",
    )
    email = models.EmailField(blank=True)
    answers = models.JSONField(default=dict, blank=True)
    scores = models.JSONField(default=dict, blank=True)
    primary_family = models.CharField(max_length=20, blank=True)
    secondary_families = models.JSONField(default=list, blank=True)
    current_question = models.PositiveSmallIntegerField(default=1)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    completed_at = models.DateTimeField(null=True, blank=True)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["email"], name="chatia_olfactory_email")]

    def __str__(self):
        return self.email or f"Test {self.pk}"


class PerfumeOlfactoryProfile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="olfactory_profiles",
    )
    email = models.EmailField(unique=True)
    test = models.ForeignKey(
        OlfactoryTest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
    )
    floral_score = models.PositiveSmallIntegerField(default=0)
    citrus_score = models.PositiveSmallIntegerField(default=0)
    oriental_score = models.PositiveSmallIntegerField(default=0)
    woody_score = models.PositiveSmallIntegerField(default=0)
    aquatic_score = models.PositiveSmallIntegerField(default=0)
    herbal_score = models.PositiveSmallIntegerField(default=0)
    fruity_score = models.PositiveSmallIntegerField(default=0)
    gourmand_score = models.PositiveSmallIntegerField(default=0)
    primary_family = models.CharField(max_length=20, blank=True)
    secondary_families = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.email
