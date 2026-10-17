from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_profile_person_profile_profile_person"),
    ]

    operations = [
        migrations.CreateModel(
            name="DataDeletionRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("confirmation_code", models.CharField(max_length=64, unique=True)),
                ("facebook_user_id", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("deleted", "Eliminada"),
                            ("absent", "Sin datos"),
                            ("kept", "Conservada"),
                        ],
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
