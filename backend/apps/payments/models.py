from django.db import models

from apps.purchases.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        APPROVED = "APPROVED", "Aprobado"
        DECLINED = "DECLINED", "Rechazado"
        VOIDED = "VOIDED", "Anulado"
        ERROR = "ERROR", "Error"

    order = models.ForeignKey(Order, related_name="payments", on_delete=models.PROTECT)
    reference = models.CharField(max_length=64, unique=True)
    amount_in_cents = models.PositiveBigIntegerField()
    currency = models.CharField(max_length=3, default="COP")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    expiration_time = models.CharField(max_length=40)
    expires_at = models.DateTimeField()
    wompi_transaction_id = models.CharField(max_length=64, blank=True)
    customer_email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} ({self.status})"
