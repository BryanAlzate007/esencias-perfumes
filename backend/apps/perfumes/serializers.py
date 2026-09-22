from django.db.models import Max
from rest_framework import serializers

from .models import Perfume


class PerfumeSerializer(serializers.ModelSerializer):
    last_review_at = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = Perfume
        fields = (
            "id",
            "name",
            "brand",
            "description",
            "notes",
            "image_url",
            "price",
            "is_active",
            "last_review_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "last_review_at")


class PerfumeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfume
        fields = ("id", "name", "brand", "description", "notes", "image_url", "price", "is_active")


def with_last_review(queryset):
    return queryset.annotate(last_review_at=Max("reviews__created_at"))
