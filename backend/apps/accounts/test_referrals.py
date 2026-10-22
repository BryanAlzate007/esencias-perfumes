from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.points import award_order_points
from apps.purchases.models import Order

User = get_user_model()


class ReferralViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="ana", password="StrongPass123!")
        self.client.force_login(self.user)

    def test_referral_stays_locked_without_a_purchase(self):
        response = self.client.get("/api/v1/referrals/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["enabled"])
        self.assertEqual(response.json()["qr_url"], "")
        self.assertEqual(response.json()["referrals"], [])

    def test_qr_is_stored_and_a_friend_purchase_is_listed(self):
        Order.objects.create(user=self.user, status=Order.Status.CONFIRMED)
        overview = self.client.get("/api/v1/referrals/")
        body = overview.json()
        self.assertTrue(body["enabled"])
        self.assertTrue(body["qr_url"])
        self.user.points_account.refresh_from_db()
        self.assertTrue(self.user.points_account.referral_qr.name)

        friend = User.objects.create_user(username="luis", password="StrongPass123!")
        self.client.force_login(friend)
        claimed = self.client.post("/api/v1/referrals/claim/", {"code": body["code"]}, format="json")
        self.assertEqual(claimed.status_code, 200, claimed.content)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get("/api/v1/referrals/").json()["referrals"], [])

        order = Order.objects.create(user=friend, status=Order.Status.CONFIRMED)
        award_order_points(order)
        listed = self.client.get("/api/v1/referrals/").json()["referrals"]
        self.assertEqual(listed[0]["username"], "luis")
        self.assertTrue(listed[0]["purchased_at"])
        self.user.points_account.refresh_from_db()
        self.assertEqual(self.user.points_account.balance, 120)

        second = Order.objects.create(user=friend, status=Order.Status.CONFIRMED)
        award_order_points(second)
        self.user.points_account.refresh_from_db()
        self.assertEqual(self.user.points_account.balance, 140)
        self.assertEqual(len(self.client.get("/api/v1/referrals/").json()["referrals"]), 1)
