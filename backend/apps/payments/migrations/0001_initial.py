import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("purchases", "0003_alter_order_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reference", models.CharField(max_length=64, unique=True)),
                ("amount_in_cents", models.PositiveBigIntegerField()),
                ("currency", models.CharField(default="COP", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "Pendiente"),
                            ("APPROVED", "Aprobado"),
                            ("DECLINED", "Rechazado"),
                            ("VOIDED", "Anulado"),
                            ("ERROR", "Error"),
                        ],
                        default="PENDING",
                        max_length=20,
                    ),
                ),
                ("expiration_time", models.CharField(max_length=40)),
                ("expires_at", models.DateTimeField()),
                ("wompi_transaction_id", models.CharField(blank=True, max_length=64)),
                ("customer_email", models.EmailField(blank=True, max_length=254)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payments",
                        to="purchases.order",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
