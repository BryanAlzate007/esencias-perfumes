from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.payments.models import Payment
from apps.payments.wompi import event_checksum, integrity_signature
from apps.perfumes.models import Container, Perfume
from apps.purchases.models import CartItem, Order

User = get_user_model()

WOMPI = {
    "WOMPI_PUBLIC_KEY": "pub_test_public",
    "WOMPI_PRIVATE_KEY": "prv_test_private",
    "WOMPI_INTEGRITY_SECRET": "test_integrity_secret",
    "WOMPI_EVENTS_SECRET": "test_events_secret",
    "WOMPI_API_URL": "https://sandbox.wompi.co/v1",
    "FRONTEND_URL": "http://localhost:5173",
}


@override_settings(**WOMPI)
class WompiPaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="ana", email="ana@example.com", password="Secret123!")
        self.other = User.objects.create_user(username="luis", email="luis@example.com", password="Secret123!")
        self.perfume = Perfume.objects.create(
            name="Aurora",
            brand="Esencias",
            description="Cítrica",
            price="10.00",
            grams=100,
            gram_price="0.20",
        )
        self.glass = Container.objects.create(
            name="Vidrio",
            description="Vidrio",
            type="Frasco",
            size="50 ml",
            weight="120 g",
            volume="50 ml",
            material="Vidrio",
            color="Ámbar",
            price="5.00",
        )

    def _cart(self, **extra):
        self.client.force_login(self.user)
        payload = {"perfume": self.perfume.id, "quantity": 2}
        payload.update(extra)
        created = self.client.post("/api/v1/cart/", payload, format="json")
        self.assertEqual(created.status_code, 201, created.content)
        return created

    def _event(self, payment, status, amount, environment="test", transaction_id="01-1532941443-49201"):
        data = {
            "transaction": {
                "id": transaction_id,
                "status": status,
                "amount_in_cents": amount,
                "reference": payment.reference,
                "currency": "COP",
            }
        }
        properties = ["transaction.id", "transaction.status", "transaction.amount_in_cents"]
        timestamp = 1530291411
        checksum = event_checksum(data, properties, timestamp, WOMPI["WOMPI_EVENTS_SECRET"])
        return {
            "event": "transaction.updated",
            "data": data,
            "environment": environment,
            "signature": {"properties": properties, "checksum": checksum, "timestamp": timestamp},
            "sent_at": "2018-07-20T16:45:05.000Z",
        }

    def test_integrity_signature_matches_the_wompi_example(self):
        signature = integrity_signature(
            "sk8-438k4-xmxm392-sn2m",
            2490000,
            "COP",
            "prod_integrity_Z5mMke9x0k8gpErbDqwrJXMqsI6SFli6",
        )
        self.assertEqual(signature, "37c8407747e595535433ef8f6a811d853cd943046624a0ec04662b17bbf33bf5")

    def test_checkout_signs_the_server_price_and_ignores_the_client_amount(self):
        self._cart()
        CartItem.objects.filter(user=self.user).update(unit_price="1.00")
        response = self.client.post(
            "/api/v1/payments/",
            {"amount_in_cents": 100, "amount": "1.00", "currency": "USD"},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.content)
        body = response.json()
        self.assertEqual(body["amount_in_cents"], 2000)
        self.assertEqual(body["amount"], "20.00")
        self.assertEqual(body["currency"], "COP")
        self.assertEqual(body["public_key"], WOMPI["WOMPI_PUBLIC_KEY"])
        self.assertEqual(
            body["signature"],
            integrity_signature(
                body["reference"],
                body["amount_in_cents"],
                body["currency"],
                WOMPI["WOMPI_INTEGRITY_SECRET"],
                body["expiration_time"],
            ),
        )
        self.assertEqual(body["redirect_url"], "http://localhost:5173/pedidos")
        raw = response.content.decode()
        self.assertNotIn(WOMPI["WOMPI_INTEGRITY_SECRET"], raw)
        self.assertNotIn(WOMPI["WOMPI_PRIVATE_KEY"], raw)
        self.assertNotIn(WOMPI["WOMPI_EVENTS_SECRET"], raw)
        order = Order.objects.get(pk=body["order_id"])
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())

    def test_container_price_is_recalculated_even_if_the_cart_was_changed(self):
        self.client.force_login(self.user)
        created = self.client.post(
            "/api/v1/cart/",
            {"perfume": self.perfume.id, "container": self.glass.id, "grams": 150, "quantity": 9},
            format="json",
        )
        self.assertEqual(created.status_code, 201, created.content)
        CartItem.objects.filter(user=self.user).update(unit_price="1.00", quantity=9)
        response = self.client.post("/api/v1/payments/", {}, format="json")
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.json()["amount_in_cents"], 1500)
        item = Order.objects.get().items.get()
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.grams, 150)
        self.assertEqual(str(item.unit_price), "15.00")

    def test_repeating_checkout_reuses_the_open_reference(self):
        self._cart()
        first = self.client.post("/api/v1/payments/", {}, format="json")
        second = self.client.post("/api/v1/payments/", {"order": first.json()["order_id"]}, format="json")
        self.assertEqual(second.status_code, 201, second.content)
        self.assertEqual(first.json()["reference"], second.json()["reference"])
        self.assertEqual(first.json()["signature"], second.json()["signature"])
        self.assertEqual(Payment.objects.count(), 1)

    def test_old_checkout_endpoint_does_not_confirm_an_unpaid_order(self):
        self._cart()
        response = self.client.post("/api/v1/orders/checkout/", {}, format="json")
        self.assertEqual(response.status_code, 201, response.content)
        self.assertIn("signature", response.json())
        self.assertEqual(Order.objects.get().status, Order.Status.PENDING)

    def test_event_without_a_valid_checksum_is_ignored(self):
        self._cart()
        started = self.client.post("/api/v1/payments/", {}, format="json")
        payment = Payment.objects.get(reference=started.json()["reference"])
        payload = self._event(payment, "APPROVED", payment.amount_in_cents)
        payload["signature"]["checksum"] = "0" * 64
        with patch("apps.payments.services.fetch_transaction") as fetch:
            response = self.client.post(
                "/api/v1/payments/wompi/events/",
                payload,
                format="json",
                HTTP_X_EVENT_CHECKSUM=payload["signature"]["checksum"],
            )
        self.assertEqual(response.status_code, 403, response.content)
        fetch.assert_not_called()
        payment.refresh_from_db()
        payment.order.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.order.status, Order.Status.PENDING)

    def test_approved_event_confirms_the_order_only_after_wompi_returns_the_same_amount(self):
        self._cart()
        started = self.client.post("/api/v1/payments/", {}, format="json")
        payment = Payment.objects.get(reference=started.json()["reference"])
        remote = {
            "id": "01-1532941443-49201",
            "amount_in_cents": 100,
            "reference": payment.reference,
            "currency": "COP",
            "status": "APPROVED",
        }
        payload = self._event(payment, "APPROVED", 100)
        with patch("apps.payments.services.fetch_transaction", return_value=remote):
            mismatch = self.client.post("/api/v1/payments/wompi/events/", payload, format="json")
        self.assertEqual(mismatch.status_code, 200, mismatch.content)
        payment.refresh_from_db()
        payment.order.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.order.status, Order.Status.PENDING)

        remote["amount_in_cents"] = payment.amount_in_cents
        payload = self._event(payment, "APPROVED", payment.amount_in_cents)
        with patch("apps.payments.services.fetch_transaction", return_value=remote):
            approved = self.client.post(
                "/api/v1/payments/wompi/events/",
                payload,
                format="json",
                HTTP_X_EVENT_CHECKSUM=payload["signature"]["checksum"],
            )
        self.assertEqual(approved.status_code, 200, approved.content)
        payment.refresh_from_db()
        payment.order.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.APPROVED)
        self.assertEqual(payment.wompi_transaction_id, remote["id"])
        self.assertEqual(payment.order.status, Order.Status.CONFIRMED)

    @patch("apps.payments.services.fetch_transaction")
    def test_sync_uses_the_wompi_transaction_and_not_the_client_status(self, fetch):
        self._cart()
        started = self.client.post("/api/v1/payments/", {}, format="json")
        payment = Payment.objects.get(reference=started.json()["reference"])
        fetch.return_value = {
            "id": "01-1532941443-49201",
            "amount_in_cents": payment.amount_in_cents,
            "reference": payment.reference,
            "currency": "COP",
            "status": "PENDING",
        }
        response = self.client.post(
            "/api/v1/payments/sync/",
            {"transaction_id": "01-1532941443-49201", "status": "APPROVED", "amount_in_cents": 100},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["status"], Payment.Status.PENDING)
        self.assertEqual(response.json()["order_status"], Order.Status.PENDING)
        payment.order.refresh_from_db()
        self.assertEqual(payment.order.status, Order.Status.PENDING)

        self.client.force_login(self.other)
        hidden = self.client.post(
            "/api/v1/payments/sync/",
            {"transaction_id": "01-1532941443-49201"},
            format="json",
        )
        self.assertEqual(hidden.status_code, 404, hidden.content)

    def test_a_paid_order_cannot_be_charged_again(self):
        self._cart()
        started = self.client.post("/api/v1/payments/", {}, format="json")
        payment = Payment.objects.get(reference=started.json()["reference"])
        remote = {
            "id": "01-1532941443-49201",
            "amount_in_cents": payment.amount_in_cents,
            "reference": payment.reference,
            "currency": "COP",
            "status": "APPROVED",
        }
        with patch("apps.payments.services.fetch_transaction", return_value=remote):
            self.client.post(
                "/api/v1/payments/wompi/events/",
                self._event(payment, "APPROVED", payment.amount_in_cents),
                format="json",
            )
        again = self.client.post("/api/v1/payments/", {"order": payment.order_id}, format="json")
        self.assertEqual(again.status_code, 400, again.content)
        self.assertEqual(Payment.objects.filter(status=Payment.Status.APPROVED).count(), 1)
