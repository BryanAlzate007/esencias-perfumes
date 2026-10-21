from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Profile
from apps.perfumes.models import Perfume
from apps.purchases.models import Order

User = get_user_model()


CONTACT_SETTINGS = {
    "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
    "EMAIL_HOST": "smtp.gmail.com",
    "EMAIL_HOST_PASSWORD": "app-password",
    "DEFAULT_FROM_EMAIL": "bryanalzate007@gmail.com",
    "CONTACT_EMAIL": "esencias.soporte@gmail.com",
}


@override_settings(**CONTACT_SETTINGS)
class ContactEmailTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_sends_distributor_request(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Ana",
                "email": "ana@example.com",
                "phone": "3001234567",
                "message": "Quiero ser distribuidor",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.subject, "Nuevo distribuidor")
        self.assertEqual(sent.to, ["esencias.soporte@gmail.com"])
        self.assertEqual(sent.from_email, "bryanalzate007@gmail.com")
        self.assertEqual(sent.reply_to, ["ana@example.com"])
        self.assertIn("Nombre: Ana", sent.body)
        self.assertIn("WhatsApp: 3001234567", sent.body)
        self.assertIn("Quiero ser distribuidor", sent.body)

    def test_rejects_an_invalid_email(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Ana",
                "email": "no-es-correo",
                "phone": "3001234567",
                "message": "Hola",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(EMAIL_HOST_PASSWORD="")
    def test_reports_when_smtp_is_not_configured(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Ana",
                "email": "ana@example.com",
                "phone": "3001234567",
                "message": "Hola",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(len(mail.outbox), 0)


class HealthCheckTests(TestCase):
    def test_health_endpoint_returns_ok(self):
        response = self.client.get(reverse("health-check"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")


class DashboardStatsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username="admin", email="admin@example.com", password="Admin1234!", is_staff=True)
        self.admin.profile.role = Profile.Role.ADMIN
        self.admin.profile.save()
        self.customer = User.objects.create_user(username="sofia", email="sofia@example.com", password="User1234!")
        self.perfume = Perfume.objects.create(
            name="Noche",
            brand="Esencias",
            description="Amaderada",
            price="80.00",
        )
        Order.objects.create(user=self.customer)

    def test_dashboard_requires_admin(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse("dashboard-stats"))
        self.assertEqual(response.status_code, 403)

    def test_dashboard_groups_users_orders_and_products(self):
        older = timezone.now() - timedelta(days=40)
        Perfume.objects.filter(pk=self.perfume.pk).update(created_at=older)
        self.client.force_login(self.admin)

        response = self.client.get(reverse("dashboard-stats"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["users"]["day"]), 30)
        self.assertEqual(len(payload["orders"]["month"]), 12)
        today = timezone.localdate().isoformat()
        users_today = next(point for point in payload["users"]["day"] if point["date"] == today)
        orders_today = next(point for point in payload["orders"]["day"] if point["date"] == today)
        self.assertGreaterEqual(users_today["value"], 2)
        self.assertEqual(orders_today["value"], 1)
        self.assertEqual(sum(point["value"] for point in payload["products"]["day"]), 0)
        month_key = older.astimezone(timezone.get_current_timezone()).strftime("%Y-%m")
        products_month = next(point for point in payload["products"]["month"] if point["date"] == month_key)
        self.assertEqual(products_month["value"], 1)
