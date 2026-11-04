import uuid

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def fill_public_ids(apps, schema_editor):
    ChatIA = apps.get_model("chatia", "ChatIA")
    for chat in ChatIA.objects.filter(public_id__isnull=True):
        chat.public_id = uuid.uuid4()
        chat.save(update_fields=["public_id"])


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("chatia", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatia",
            name="public_id",
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(fill_public_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="chatia",
            name="public_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name="chatia",
            name="advisor_name",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="chatia",
            name="language",
            field=models.CharField(default="es", max_length=8),
        ),
        migrations.AddField(
            model_name="chatia",
            name="email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="message",
            name="role",
            field=models.CharField(
                choices=[("user", "Cliente"), ("assistant", "Asesor")],
                default="user",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="chatia",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="messages",
                to="chatia.chatia",
            ),
        ),
        migrations.AlterModelOptions(
            name="message",
            options={"ordering": ["created_at", "id"]},
        ),
        migrations.CreateModel(
            name="OlfactoryTest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("answers", models.JSONField(blank=True, default=dict)),
                ("scores", models.JSONField(blank=True, default=dict)),
                ("primary_family", models.CharField(blank=True, max_length=20)),
                ("secondary_families", models.JSONField(blank=True, default=list)),
                ("current_question", models.PositiveSmallIntegerField(default=1)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("in_progress", "En curso"),
                            ("awaiting_email", "Esperando correo"),
                            ("completed", "Completado"),
                        ],
                        default="in_progress",
                        max_length=20,
                    ),
                ),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("email_sent_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "chat",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="olfactory_test",
                        to="chatia.chatia",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="olfactory_tests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="olfactorytest",
            index=models.Index(fields=["email"], name="chatia_olfactory_email"),
        ),
        migrations.CreateModel(
            name="PerfumeOlfactoryProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("floral_score", models.PositiveSmallIntegerField(default=0)),
                ("citrus_score", models.PositiveSmallIntegerField(default=0)),
                ("oriental_score", models.PositiveSmallIntegerField(default=0)),
                ("woody_score", models.PositiveSmallIntegerField(default=0)),
                ("aquatic_score", models.PositiveSmallIntegerField(default=0)),
                ("herbal_score", models.PositiveSmallIntegerField(default=0)),
                ("fruity_score", models.PositiveSmallIntegerField(default=0)),
                ("gourmand_score", models.PositiveSmallIntegerField(default=0)),
                ("primary_family", models.CharField(blank=True, max_length=20)),
                ("secondary_families", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "test",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="profiles",
                        to="chatia.olfactorytest",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="olfactory_profiles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-updated_at"]},
        ),
    ]
