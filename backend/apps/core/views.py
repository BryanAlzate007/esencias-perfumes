from datetime import datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminRole
from apps.perfumes.models import Perfume
from apps.purchases.models import Order

User = get_user_model()
DAY_WINDOW = 30
MONTH_WINDOW = 12


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
