from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("perfumes", "0004_container_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfume",
            name="grams",
            field=models.IntegerField(default=100),
        ),
    ]
