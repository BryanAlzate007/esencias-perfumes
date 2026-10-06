from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("perfumes", "0003_main_chords_perfume_color_perfume_price_usd_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="container",
            name="price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
