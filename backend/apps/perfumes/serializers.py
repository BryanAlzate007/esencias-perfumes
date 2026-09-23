from django.db.models import Max
from rest_framework import serializers

from .models import Container, Main_chords, Perfume

PERFUME_FIELDS = (
    "id",
    "name",
    "brand",
    "description",
    "notes",
    "image_url",
    "price",
    "price_usd",
    "color",
    "main_chords",
    "is_active",
)


class MainChordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Main_chords
        fields = ("id", "name", "description")


class ContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Container
        fields = (
            "id",
            "name",
            "description",
            "image_url",
            "type",
            "size",
            "weight",
            "volume",
            "material",
            "color",
            "main_chords",
            "is_active",
        )


class PerfumeSerializer(serializers.ModelSerializer):
    last_review_at = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = Perfume
        fields = (*PERFUME_FIELDS, "last_review_at", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at", "last_review_at")


class PerfumeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfume
        fields = PERFUME_FIELDS


def with_last_review(queryset):
    return queryset.annotate(last_review_at=Max("reviews__created_at"))
