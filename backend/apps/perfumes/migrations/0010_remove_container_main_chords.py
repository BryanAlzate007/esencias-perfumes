from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("perfumes", "0009_perfumecontainerprice"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="container",
            name="main_chords",
        ),
    ]
