import django.db.models.deletion
from django.db import migrations, models


def fill_cart_prices(apps, schema_editor):
    CartItem = apps.get_model("purchases", "CartItem")
    for item in CartItem.objects.select_related("perfume"):
        item.unit_price = item.perfume.price
        item.save(update_fields=["unit_price"])


class Migration(migrations.Migration):

    dependencies = [
        ("perfumes", "0004_container_price"),
        ("purchases", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cartitem",
            name="container",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cart_items",
                to="perfumes.container",
            ),
        ),
        migrations.AddField(
            model_name="cartitem",
            name="grams",
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.AddField(
            model_name="cartitem",
            name="unit_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="container",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="order_items",
                to="perfumes.container",
            ),
        ),
        migrations.AddField(
            model_name="orderitem",
            name="grams",
            field=models.PositiveIntegerField(default=5),
        ),
        migrations.RunPython(fill_cart_prices, migrations.RunPython.noop),
        migrations.AlterUniqueTogether(
            name="cartitem",
            unique_together={("user", "perfume", "container")},
        ),
    ]
