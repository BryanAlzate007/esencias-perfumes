from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("perfumes", "0010_remove_container_main_chords"),
    ]

    operations = [
        migrations.AddField(
            model_name="perfume",
            name="kind",
            field=models.CharField(
                choices=[("perfume", "Perfume"), ("candle", "Vela")],
                default="perfume",
                max_length=20,
            ),
        ),
    ]
