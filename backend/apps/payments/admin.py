from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "order", "amount_in_cents", "currency", "status", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("reference", "wompi_transaction_id", "customer_email")
    readonly_fields = (
        "order",
        "reference",
        "amount_in_cents",
        "currency",
        "expiration_time",
        "expires_at",
        "wompi_transaction_id",
        "customer_email",
        "created_at",
        "updated_at",
    )
