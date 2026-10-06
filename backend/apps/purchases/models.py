from django.conf import settings
from django.db import models

from apps.perfumes.models import Container, Perfume


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="cart_items", on_delete=models.CASCADE)
    perfume = models.ForeignKey(Perfume, related_name="cart_items", on_delete=models.CASCADE)
    container = models.ForeignKey(
        Container,
        related_name="cart_items",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(default=1)
    grams = models.PositiveIntegerField(default=5)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "perfume", "container")

    def __str__(self):
        return f"{self.user} cart {self.perfume} x{self.quantity}"


class Order(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        PENDING = "pending", "Pendiente"
        CONFIRMED = "confirmed", "Confirmado"
        CANCELLED = "cancelled", "Cancelado"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} by {self.user}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    perfume = models.ForeignKey(Perfume, related_name="order_items", on_delete=models.PROTECT)
    container = models.ForeignKey(
        Container,
        related_name="order_items",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField(default=1)
    grams = models.PositiveIntegerField(default=5)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
