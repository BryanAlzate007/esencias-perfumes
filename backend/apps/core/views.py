import logging
from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminRole
from apps.perfumes.models import Perfume
from apps.purchases.models import Order

User = get_user_model()
logger = logging.getLogger(__name__)
DAY_WINDOW = 30
MONTH_WINDOW = 12
CONTACT_SUBJECT = "Nuevo distribuidor"
CONTACT_LIMIT = 8
CONTACT_WINDOW_SECONDS = 10 * 60


def _shift_month(year, month, delta):
    index = year * 12 + (month - 1) + delta
    return index // 12, index % 12 + 1


def _buckets(period):
    today = timezone.localdate()
    if period == "day":
        start = today - timedelta(days=DAY_WINDOW - 1)
        keys = [(start + timedelta(days=offset)).isoformat() for offset in range(DAY_WINDOW)]
        return start, keys

    year, month = _shift_month(today.year, today.month, -(MONTH_WINDOW - 1))
    keys = []
    for offset in range(MONTH_WINDOW):
        bucket_year, bucket_month = _shift_month(year, month, offset)
        keys.append(f"{bucket_year:04d}-{bucket_month:02d}")
    return today.replace(year=year, month=month, day=1), keys


def _bucket_key(bucket, period):
    if isinstance(bucket, datetime):
        if timezone.is_aware(bucket):
            bucket = timezone.localtime(bucket)
        bucket = bucket.date()
    if period == "month":
        return f"{bucket.year:04d}-{bucket.month:02d}"
    return bucket.isoformat()


def _series(queryset, field, period):
    start, keys = _buckets(period)
    start_at = timezone.make_aware(datetime.combine(start, time.min))
    trunc = TruncDate(field) if period == "day" else TruncMonth(field)
    rows = (
        queryset.filter(**{f"{field}__gte": start_at})
        .annotate(bucket=trunc)
        .values("bucket")
        .annotate(value=Count("id"))
        .order_by("bucket")
    )
    found = {_bucket_key(row["bucket"], period): row["value"] for row in rows}
    return [{"date": key, "value": int(found.get(key, 0))} for key in keys]


def _contact_field(value, limit):
    text = " ".join(str(value or "").split())
    return text[:limit]


def _contact_limited(request):
    address = request.META.get("REMOTE_ADDR") or "unknown"
    key = f"contact-email:{address}"
    sent = cache.get(key, 0)
    if sent >= CONTACT_LIMIT:
        return True
    cache.set(key, sent + 1, CONTACT_WINDOW_SECONDS)
    return False


class ContactView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        name = _contact_field(request.data.get("name"), 120)
        email = _contact_field(request.data.get("email"), 254)
        phone = _contact_field(request.data.get("phone"), 40)
        message = str(request.data.get("message") or "").strip()[:4000]
        if not name or not email or not phone or not message:
            return Response({"detail": "Completa todos los campos."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_email(email)
        except ValidationError:
            return Response({"detail": "El correo no es válido."}, status=status.HTTP_400_BAD_REQUEST)
        if _contact_limited(request):
            return Response({"detail": "Espera un momento antes de enviar otro mensaje."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        if not settings.EMAIL_HOST or not settings.EMAIL_HOST_PASSWORD:
            logger.error("Contact form email was not sent because SMTP credentials are missing.")
            return Response(
                {"detail": "No pudimos enviar el mensaje. El correo del sitio no está configurado."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        body = "\n".join([
            f"Nombre: {name}",
            f"Correo: {email}",
            f"WhatsApp: {phone}",
            "",
            message,
        ])
        mail = EmailMessage(
            subject=CONTACT_SUBJECT,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL],
            reply_to=[email],
        )
        try:
            mail.send(fail_silently=False)
        except Exception:
            logger.exception("Contact form email failed.")
            return Response(
                {"detail": "No pudimos enviar el mensaje. Intenta de nuevo."},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"detail": "ok"})


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "status": "ok",
                "service": "perfume-platform",
                "version": "v1",
            }
        )


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        metrics = {
            "users": (User.objects.all(), "date_joined"),
            "orders": (Order.objects.all(), "created_at"),
            "products": (Perfume.objects.all(), "created_at"),
        }
        payload = {}
        for name, (queryset, field) in metrics.items():
            payload[name] = {
                "day": _series(queryset, field, "day"),
                "month": _series(queryset, field, "month"),
            }
        return Response(payload)
