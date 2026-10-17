import base64
import hashlib
import hmac
import json
from datetime import timedelta

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import DataDeletionRequest, Profile
from apps.payments.models import Payment
from apps.perfumes.models import Perfume
from apps.purchases.models import CartItem, Order
from apps.reviews.models import Review

User = get_user_model()
SECRET = "facebook-test-secret"


def signed_request(payload, secret=SECRET):
    raw = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = hmac.new(secret.encode(), raw.encode(), hashlib.sha256).digest()
    encoded = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{encoded}.{raw}"


@override_settings(FACEBOOK_CLIENT_SECRET=SECRET)
class FacebookDataDeletionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="camila",
            email="camila@example.com",
            password="User1234!",
            first_name="Camila",
        )
        self.user.profile.phone = "+573001112233"
        self.user.profile.save()
        SocialAccount.objects.create(user=self.user, provider="facebook", uid="998877", extra_data={"email": "camila@example.com"})
        self.perfume = Perfume.objects.create(
            name="Noche",
            brand="Esencias",
            description="Amaderada",
            price="80.00",
        )
        CartItem.objects.create(user=self.user, perfume=self.perfume, quantity=1, grams=5, unit_price="10.00")
        Review.objects.create(user=self.user, perfume=self.perfume, body="Me gusta")
        order = Order.objects.create(user=self.user, status=Order.Status.CONFIRMED)
        Payment.objects.create(
            order=order,
            reference="esencias-test-1",
            amount_in_cents=8000000,
            status=Payment.Status.APPROVED,
            expiration_time="2030-01-01T00:00:00Z",
            expires_at=timezone.now() + timedelta(minutes=20),
            customer_email="camila@example.com",
        )

    def test_signed_request_deletes_account_and_keeps_the_sale(self):
        response = self.client.post(
            "/users/deletedates",
            data={"signed_request": signed_request({"algorithm": "HMAC-SHA256", "user_id": "998877"})},
        )
        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        self.assertIn("confirmation_code", body)
        self.assertIn(f"code={body['confirmation_code']}", body["url"])

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(self.user.email, "")
        self.assertEqual(self.user.first_name, "")
        self.assertEqual(self.user.username, f"deleted-{self.user.pk}")
        self.assertFalse(self.user.has_usable_password())
        self.assertEqual(self.user.profile.phone, "")
        self.assertFalse(SocialAccount.objects.filter(uid="998877").exists())
        self.assertFalse(self.user.cart_items.exists())
        self.assertFalse(self.user.reviews.exists())
        self.assertEqual(self.user.orders.count(), 1)
        self.assertEqual(self.user.orders.get().payments.get().customer_email, "")

        status_page = self.client.get(f"/users/deletedates?code={body['confirmation_code']}")
        self.assertEqual(status_page.status_code, 200)
        self.assertContains(status_page, body["confirmation_code"])
        self.assertEqual(
            DataDeletionRequest.objects.get(confirmation_code=body["confirmation_code"]).status,
            DataDeletionRequest.Status.DELETED,
        )

    def test_unknown_facebook_user_still_confirms(self):
        response = self.client.post(
            "/users/deletedates",
            data={"signed_request": signed_request({"algorithm": "HMAC-SHA256", "user_id": "000"})},
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertEqual(
            DataDeletionRequest.objects.get(confirmation_code=response.json()["confirmation_code"]).status,
            DataDeletionRequest.Status.ABSENT,
        )

    def test_bad_signature_is_rejected(self):
        response = self.client.post(
            "/users/deletedates",
            data={"signed_request": signed_request({"algorithm": "HMAC-SHA256", "user_id": "998877"}, secret="otra")},
        )
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "camila@example.com")
        self.assertFalse(DataDeletionRequest.objects.exists())

    def test_admin_account_is_not_erased(self):
        self.user.is_staff = True
        self.user.save(update_fields=["is_staff"])
        self.user.profile.role = Profile.Role.ADMIN
        self.user.profile.save(update_fields=["role"])
        response = self.client.post(
            "/users/deletedates",
            data={"signed_request": signed_request({"algorithm": "HMAC-SHA256", "user_id": "998877"})},
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "camila@example.com")
        self.assertTrue(SocialAccount.objects.filter(uid="998877").exists())
        self.assertEqual(
            DataDeletionRequest.objects.get().status,
            DataDeletionRequest.Status.KEPT,
        )
