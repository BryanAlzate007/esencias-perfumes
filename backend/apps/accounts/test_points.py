from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import PointEntry, PointsAccount, Referral
from apps.purchases.models import Order

User = get_user_model()


class PointsAndReferralTests(TestCase):
    def setUp(self):
        self.referrer = User.objects.create_user(username="referidor", password="StrongPass123!")
        self.referred = User.objects.create_user(username="referido", password="StrongPass123!")
        self.account = self.referrer.points_account

    def test_points_stay_disabled_until_the_first_purchase(self):
        self.assertFalse(self.account.enabled)
        self.assertEqual(self.account.balance, 0)
        self.assertEqual(len(self.account.referral_code), 8)
        order = Order.objects.create(user=self.referrer, status=Order.Status.CONFIRMED)

        with self.assertRaises(ValidationError):
            self.account.add_points(20, PointEntry.Source.PURCHASE, order=order)
        with self.assertRaises(ValidationError):
            Referral.refer(self.referrer, self.referred, 15)

    def test_redeem_resets_balance_and_keeps_origin_and_state_dates(self):
        order = Order.objects.create(user=self.referrer, status=Order.Status.CONFIRMED)
        self.account.enable()
        purchase = self.account.add_points(20, PointEntry.Source.PURCHASE, order=order)
        Referral.refer(self.referrer, self.referred, 15)

        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 35)

        redemption = self.account.redeem()
        self.account.refresh_from_db()
        purchase.refresh_from_db()

        self.assertEqual(self.account.balance, 0)
        self.assertEqual(redemption.points, 35)
        self.assertEqual(purchase.status, PointEntry.Status.REDEEMED)
        self.assertEqual(purchase.source, PointEntry.Source.PURCHASE)
        self.assertEqual(purchase.order_id, order.id)
        self.assertIsNotNone(purchase.redeemed_at)

        states = list(purchase.events.values_list("status", flat=True))
        self.assertEqual(states, [PointEntry.Status.AVAILABLE, PointEntry.Status.REDEEMED])
        self.assertTrue(all(purchase.events.values_list("created_at", flat=True)))

        referral_entry = self.account.entries.get(source=PointEntry.Source.REFERRAL)
        self.assertEqual(referral_entry.points, 15)
        self.assertEqual(referral_entry.status, PointEntry.Status.REDEEMED)
        referral = Referral.objects.get(referrer=self.referrer, referred=self.referred)
        self.assertEqual(referral.status, Referral.Status.CREDITED)
        self.assertEqual(
            list(referral.events.values_list("status", flat=True)),
            [Referral.Status.PENDING, Referral.Status.CREDITED],
        )

        self.account.redeem()
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, 0)
        self.assertEqual(self.account.entries.count(), 2)
