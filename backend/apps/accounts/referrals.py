import io

import qrcode
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import PointEntry, PointsAccount, Referral, ReferralEvent

REFERRAL_PURCHASE_POINTS = 20


def referral_share_url(account):
    return f"{settings.FRONTEND_URL}/registro?ref={account.referral_code}"


def ensure_referral_qr(account):
    if account is None or not account.enabled or account.referral_qr:
        return account
    image = qrcode.make(referral_share_url(account))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    account.referral_qr.save(
        f"{account.referral_code}.png",
        ContentFile(buffer.getvalue()),
        save=True,
    )
    return account


def claim_referral(user, code):
    normalized = (code or "").strip().upper()
    if not normalized:
        raise ValidationError("El código de referido no es válido.")
    account = (
        PointsAccount.objects.filter(referral_code=normalized, enabled=True)
        .select_related("user")
        .first()
    )
    if account is None or account.user_id == user.pk:
        raise ValidationError("El código de referido no es válido.")
    existing = Referral.objects.filter(referred=user).first()
    if existing is not None:
        return existing
    try:
        with transaction.atomic():
            return Referral.objects.create(
                referrer=account.user,
                referred=user,
                code=account.referral_code,
                status=Referral.Status.PENDING,
            )
    except IntegrityError as exc:
        raise ValidationError("Este usuario ya fue referido.") from exc


def award_referrer_for_purchase(order):
    referral = (
        Referral.objects.select_related("referrer")
        .filter(referred_id=order.user_id)
        .first()
    )
    if referral is None:
        return None
    if PointEntry.objects.filter(
        referral=referral,
        order=order,
        source=PointEntry.Source.REFERRAL,
    ).exists():
        return None
    try:
        account = referral.referrer.points_account
    except PointsAccount.DoesNotExist:
        return None
    if not account.enabled:
        return None
    account.add_points(
        REFERRAL_PURCHASE_POINTS,
        PointEntry.Source.REFERRAL,
        order=order,
        referral=referral,
    )
    referral.points_awarded += REFERRAL_PURCHASE_POINTS
    update_fields = ["points_awarded", "updated_at"]
    if referral.status != Referral.Status.CREDITED:
        referral.status = Referral.Status.CREDITED
        referral.purchased_at = order.created_at or timezone.now()
        update_fields.extend(["status", "purchased_at"])
        referral.save(update_fields=update_fields)
        ReferralEvent.objects.create(referral=referral, status=Referral.Status.CREDITED)
    else:
        referral.save(update_fields=update_fields)
    return referral
