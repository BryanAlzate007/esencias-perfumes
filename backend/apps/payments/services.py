import logging
import uuid
from datetime import timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.purchases.models import CartItem, Order, OrderItem
from apps.purchases.pricing import line_total, money

from .models import Payment
from .wompi import WompiRequestError, fetch_transaction, integrity_signature, verify_event

logger = logging.getLogger(__name__)

CURRENCY = "COP"
CHECKOUT_TTL = timedelta(minutes=20)
UTC = ZoneInfo("UTC")


class PaymentError(Exception):
    status_code = 400
    detail = "No se pudo iniciar el pago."

    def __init__(self, detail=None, status_code=None):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.detail)


class EmptyCart(PaymentError):
    detail = "El carrito está vacío."


class OrderNotPayable(PaymentError):
    status_code = 404
    detail = "Pedido no encontrado."


class AlreadyPaid(PaymentError):
    detail = "Este pedido ya fue pagado."


class UnavailableProduct(PaymentError):
    detail = "Hay productos que ya no están disponibles."


class GatewayNotConfigured(PaymentError):
    status_code = 503
    detail = "La pasarela de pagos no está configurada."


class AmountMismatch(PaymentError):
    detail = "El monto confirmado por Wompi no coincide con el pedido."


class InvalidSignature(PaymentError):
    status_code = 403
    detail = "Firma de evento inválida."


def _configured(*values):
    return all(value not in (None, "") for value in values)


def ensure_checkout_configured():
    if not _configured(settings.WOMPI_PUBLIC_KEY, settings.WOMPI_PRIVATE_KEY, settings.WOMPI_INTEGRITY_SECRET):
        raise GatewayNotConfigured()


def amount_in_cents(total):
    cents = int((money(total) * 100).to_integral_value())
    if cents <= 0:
        raise PaymentError("El valor del pedido no es válido.")
    return cents


def order_total(order):
    total = Decimal("0")
    items = list(order.items.all())
    if not items:
        raise PaymentError("El pedido no tiene productos.")
    for item in items:
        total += money(item.unit_price) * item.quantity
    return money(total)


def expiration_stamp(moment):
    return moment.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def session_payload(payment):
    ensure_checkout_configured()
    signature = integrity_signature(
        payment.reference,
        payment.amount_in_cents,
        payment.currency,
        settings.WOMPI_INTEGRITY_SECRET,
        payment.expiration_time,
    )
    return {
        "order_id": payment.order_id,
        "reference": payment.reference,
        "currency": payment.currency,
        "amount_in_cents": payment.amount_in_cents,
        "amount": format(money(Decimal(payment.amount_in_cents) / Decimal("100")), ".2f"),
        "public_key": settings.WOMPI_PUBLIC_KEY,
        "signature": signature,
        "redirect_url": f"{settings.FRONTEND_URL}/pedidos",
        "expiration_time": payment.expiration_time,
        "customer_email": payment.customer_email,
    }


def _quoted_line(item):
    perfume = item.perfume
    if not perfume.is_active:
        raise UnavailableProduct()
    container = item.container
    if container is not None:
        if not container.is_active:
            raise UnavailableProduct()
        grams, unit_price = line_total(perfume, container, item.grams)
        return grams, 1, unit_price
    _, unit_price = line_total(perfume, None, perfume.grams)
    quantity = item.quantity or 0
    if quantity < 1:
        raise PaymentError("La cantidad del carrito no es válida.")
    return item.grams, quantity, unit_price


@transaction.atomic
def snapshot_cart(user):
    items = list(
        CartItem.objects.select_for_update(of=("self",))
        .filter(user=user)
        .select_related("perfume", "container")
    )
    if not items:
        raise EmptyCart()
    order = Order.objects.create(user=user, status=Order.Status.PENDING)
    for item in items:
        grams, quantity, unit_price = _quoted_line(item)
        OrderItem.objects.create(
            order=order,
            perfume=item.perfume,
            container=item.container,
            quantity=quantity,
            grams=grams,
            unit_price=unit_price,
        )
    CartItem.objects.filter(pk__in=[item.pk for item in items]).delete()
    return order


def _open_payment(order, user):
    order = Order.objects.select_for_update().get(pk=order.pk)
    if order.status == Order.Status.CONFIRMED or Payment.objects.filter(order=order, status=Payment.Status.APPROVED).exists():
        raise AlreadyPaid()
    if order.status != Order.Status.PENDING:
        raise OrderNotPayable()
    current = (
        Payment.objects.filter(order=order, status=Payment.Status.PENDING, expires_at__gt=timezone.now())
        .order_by("-created_at")
        .first()
    )
    if current is not None:
        return current
    Payment.objects.filter(order=order, status=Payment.Status.PENDING, expires_at__lte=timezone.now()).update(
        status=Payment.Status.ERROR
    )
    expires_at = (timezone.now() + CHECKOUT_TTL).replace(microsecond=0)
    email = (user.email or "").strip()
    return Payment.objects.create(
        order=order,
        reference=f"esencias-{order.pk}-{uuid.uuid4().hex[:12]}",
        amount_in_cents=amount_in_cents(order_total(order)),
        currency=CURRENCY,
        expiration_time=expiration_stamp(expires_at),
        expires_at=expires_at,
        customer_email=email,
    )


@transaction.atomic
def start_payment(user, order_id=None):
    ensure_checkout_configured()
    if order_id is None:
        order = snapshot_cart(user)
    else:
        order = Order.objects.select_for_update().filter(pk=order_id, user=user).first()
        if order is None:
            raise OrderNotPayable()
        if order.status == Order.Status.CONFIRMED:
            raise AlreadyPaid()
        if order.status != Order.Status.PENDING:
            raise OrderNotPayable()
    return _open_payment(order, user)


def _as_cents(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise AmountMismatch() from None


@transaction.atomic
def apply_verified_transaction(payment, transaction):
    locked = Payment.objects.select_for_update().select_related("order").get(pk=payment.pk)
    if locked.status == Payment.Status.APPROVED:
        return locked
    remote_amount = _as_cents(transaction.get("amount_in_cents"))
    status = transaction.get("status")
    matches = (
        transaction.get("reference") == locked.reference
        and transaction.get("currency") == locked.currency
        and remote_amount == locked.amount_in_cents
        and status in Payment.Status.values
    )
    wompi_id = str(transaction.get("id") or "")[:64]
    if not matches:
        logger.warning("Wompi transaction did not match payment %s", locked.reference)
        raise AmountMismatch()
    locked.status = status
    if wompi_id:
        locked.wompi_transaction_id = wompi_id
    locked.save(update_fields=["status", "wompi_transaction_id", "updated_at"])
    if status == Payment.Status.APPROVED:
        updated = Order.objects.filter(pk=locked.order_id, status=Order.Status.PENDING).update(
            status=Order.Status.CONFIRMED
        )
        if updated:
            locked.order.status = Order.Status.CONFIRMED
    return locked


def sync_transaction(user, transaction_id):
    ensure_checkout_configured()
    try:
        remote = fetch_transaction(transaction_id)
    except WompiRequestError as error:
        if error.status_code == 404:
            raise OrderNotPayable("Transacción no encontrada.") from error
        raise GatewayNotConfigured("No se pudo confirmar la transacción con Wompi.") from error
    payment = Payment.objects.filter(reference=remote.get("reference"), order__user=user).first()
    if payment is None:
        raise OrderNotPayable()
    return apply_verified_transaction(payment, remote)


def handle_event(payload, header_checksum):
    if not _configured(settings.WOMPI_EVENTS_SECRET, settings.WOMPI_PRIVATE_KEY):
        raise GatewayNotConfigured()
    if not verify_event(payload, header_checksum):
        raise InvalidSignature()
    if payload.get("event") != "transaction.updated":
        return None
    transaction = payload.get("data", {}).get("transaction")
    if not isinstance(transaction, dict):
        raise InvalidSignature()
    payment = Payment.objects.filter(reference=transaction.get("reference")).first()
    if payment is None:
        return None
    try:
        remote = fetch_transaction(str(transaction.get("id") or ""))
    except WompiRequestError as error:
        if error.status_code == 400:
            raise InvalidSignature() from error
        raise GatewayNotConfigured("No se pudo confirmar la transacción con Wompi.") from error
    if remote.get("id") != transaction.get("id"):
        raise AmountMismatch()
    try:
        return apply_verified_transaction(payment, remote)
    except AmountMismatch:
        return None
