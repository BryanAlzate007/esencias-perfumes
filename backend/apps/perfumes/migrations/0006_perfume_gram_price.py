from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("perfumes", "0005_perfume_grams"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfume",
            name="gram_price",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
