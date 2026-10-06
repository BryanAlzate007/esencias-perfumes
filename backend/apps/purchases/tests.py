from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.perfumes.models import Container, Perfume
from apps.purchases.models import CartItem, Order

User = get_user_model()


class DraftQuoteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="ana", email="ana@example.com", password="Secret123!")
        self.perfume = Perfume.objects.create(
            name="Aurora",
            brand="Esencias",
            description="Cítrica",
            price="10.00",
            grams=100,
            gram_price="0.20",
        )
        self.glass = self._container("Vidrio", "5.00")
        self.metal = self._container("Metal", "8.00")

    def _container(self, name, price):
        return Container.objects.create(
            name=name,
            description=name,
            type="Frasco",
            size="50 ml",
            weight="120 g",
            volume="50 ml",
            material="Vidrio",
            color="Ámbar",
            price=price,
        )

    def test_selecting_container_and_grams_recalculates_on_the_server(self):
        self.client.force_login(self.user)
        draft = self.client.post("/api/v1/orders/draft/", {"perfume": self.perfume.id}, format="json")
        self.assertEqual(draft.status_code, 201, draft.content)
        body = draft.json()
        self.assertEqual(body["base_grams"], 100)
        self.assertEqual(body["grams"], 100)
        self.assertIsNone(body["selected_container"])
        self.assertEqual(body["perfume"]["price"], "10.00")
        self.assertEqual(body["total"], "10.00")
        self.assertEqual(len(body["containers"]), 2)
        self.assertNotIn("price", body["containers"][0])
        self.assertTrue(Order.objects.filter(pk=body["order_id"], status=Order.Status.DRAFT).exists())

        listed = self.client.get("/api/v1/orders/")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(listed.json()["results"], [])

        quoted = self.client.patch(
            f"/api/v1/orders/{body['order_id']}/quote/",
            {"container": self.glass.id, "grams": 150},
            format="json",
        )
        self.assertEqual(quoted.status_code, 200, quoted.content)
        payload = quoted.json()
        self.assertEqual(payload["selected_container"], self.glass.id)
        self.assertEqual(payload["grams"], 150)
        self.assertEqual(payload["total"], "15.00")
        self.assertEqual(payload["perfume"]["price"], "10.00")

        original = self.client.patch(
            f"/api/v1/orders/{body['order_id']}/quote/",
            {"container": None},
            format="json",
        )
        self.assertEqual(original.status_code, 200, original.content)
        self.assertIsNone(original.json()["selected_container"])
        self.assertEqual(original.json()["total"], "10.00")
        self.assertEqual(original.json()["grams"], 100)

        selected = self.client.patch(
            f"/api/v1/orders/{body['order_id']}/quote/",
            {"container": self.glass.id, "grams": 150},
            format="json",
        )
        self.assertEqual(selected.status_code, 200, selected.content)

        confirmed = self.client.post(f"/api/v1/orders/{body['order_id']}/confirm/")
        self.assertEqual(confirmed.status_code, 201, confirmed.content)
        self.assertEqual(confirmed.json()["price"], "15.00")
        self.assertEqual(confirmed.json()["grams"], 150)
        self.assertEqual(CartItem.objects.filter(user=self.user, container=self.glass).count(), 1)
        self.assertFalse(Order.objects.filter(pk=body["order_id"]).exists())

    def test_grams_below_the_perfume_base_stay_at_the_base(self):
        self.client.force_login(self.user)
        draft = self.client.post("/api/v1/orders/draft/", {"perfume": self.perfume.id}, format="json")
        order_id = draft.json()["order_id"]
        quoted = self.client.patch(
            f"/api/v1/orders/{order_id}/quote/",
            {"container": self.metal.id, "grams": 40},
            format="json",
        )
        self.assertEqual(quoted.status_code, 200, quoted.content)
        self.assertEqual(quoted.json()["grams"], 100)
        self.assertEqual(quoted.json()["total"], "8.00")
