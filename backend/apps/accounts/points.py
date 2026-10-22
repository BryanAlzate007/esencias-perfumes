from django.db.models import Q

from apps.purchases.models import Order

from .models import PointEntry, PointsAccount

from .referrals import award_referrer_for_purchase, ensure_referral_qr

FIRST_PURCHASE_POINTS = 100
REPEAT_PURCHASE_POINTS = 100


def award_order_points(order):
    order.refresh_from_db(fields=["status", "user_id", "created_at"])
    if order.status != Order.Status.CONFIRMED:
        return None

    entry = None
    if not PointEntry.objects.filter(order=order, source=PointEntry.Source.PURCHASE).exists():
        account, _ = PointsAccount.objects.get_or_create(user_id=order.user_id)
        if not account.enabled:
            account.enable()
        has_earlier_purchase = (
            Order.objects.filter(user_id=order.user_id, status=Order.Status.CONFIRMED)
            .exclude(pk=order.pk)
            .filter(Q(created_at__lt=order.created_at) | Q(created_at=order.created_at, pk__lt=order.pk))
            .exists()
        )
        points = REPEAT_PURCHASE_POINTS if has_earlier_purchase else FIRST_PURCHASE_POINTS
        entry = account.add_points(points, PointEntry.Source.PURCHASE, order=order)
        ensure_referral_qr(account)
    award_referrer_for_purchase(order)
    return entry


def sync_purchase_points(user):
    """Si ya compró y aún no tiene puntos de compra, acredita la primera."""
    account = PointsAccount.objects.filter(user=user).first()
    if PointEntry.objects.filter(account__user=user, source=PointEntry.Source.PURCHASE).exists():
        if account and not account.enabled:
            account.enable()
        return account
    first = (
        Order.objects.filter(user=user, status=Order.Status.CONFIRMED)
        .order_by("created_at", "pk")
        .first()
    )
    if first is None:
        return account
    return award_order_points(first)
