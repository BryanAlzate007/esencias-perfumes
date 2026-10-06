import json

from django.db.models import Max
from rest_framework import serializers

from .models import Container, Main_chords, Perfume, PerfumeImage

PERFUME_FIELDS = (
    "id",
    "name",
    "brand",
    "description",
    "notes",
    "catalog",
    "price",
    "price_usd",
    "color",
    "grams",
    "gram_price",
    "main_chords",
    "is_active",
)


class MainChordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Main_chords
        fields = ("id", "name", "description")


class OptionalDecimalField(serializers.DecimalField):
    def to_internal_value(self, data):
        if data in ("", None):
            return None
        return super().to_internal_value(data)


class ExplicitBooleanField(serializers.BooleanField):
    def get_value(self, dictionary):
        if self.field_name not in dictionary:
            return serializers.empty
        return dictionary.get(self.field_name)


class MainChordField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = json.loads(data) if data else []
        if not isinstance(data, list):
            raise serializers.ValidationError("Se esperaba una lista de acordes.")
        ids = []
        for item in data:
            try:
                ids.append(int(item))
            except (TypeError, ValueError) as exc:
                raise serializers.ValidationError("Acorde inválido.") from exc
        chords = list(Main_chords.objects.filter(id__in=ids))
        if len(chords) != len(set(ids)):
            raise serializers.ValidationError("Acorde no encontrado.")
        return chords

    def to_representation(self, value):
        if hasattr(value, "values_list"):
            return list(value.values_list("id", flat=True))
        return [item.pk for item in value]


class PerfumeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfumeImage
        fields = ("id", "image", "alt_text", "is_primary", "order")
        read_only_fields = fields


class PerfumeSerializer(serializers.ModelSerializer):
    images = PerfumeImageSerializer(many=True, read_only=True)
    image_url = serializers.ReadOnlyField()
    last_review_at = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = Perfume
        fields = (*PERFUME_FIELDS, "images", "image_url", "last_review_at", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at", "last_review_at", "image_url")


class PerfumeWriteSerializer(serializers.ModelSerializer):
    price_usd = OptionalDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    is_active = ExplicitBooleanField(required=False)
    main_chords = MainChordField(required=False)
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    remove_image_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)

    class Meta:
        model = Perfume
        fields = (*PERFUME_FIELDS, "images", "remove_image_ids")

    def create(self, validated_data):
        uploads = validated_data.pop("images", [])
        validated_data.pop("remove_image_ids", None)
        perfume = super().create(validated_data)
        self._store_images(perfume, uploads)
        return perfume

    def update(self, instance, validated_data):
        uploads = validated_data.pop("images", [])
        remove_ids = validated_data.pop("remove_image_ids", [])
        perfume = super().update(instance, validated_data)
        if remove_ids:
            for image in perfume.images.filter(id__in=remove_ids):
                image.image.delete(save=False)
                image.delete()
        self._store_images(perfume, uploads)
        self._ensure_primary(perfume)
        return perfume

    def _store_images(self, perfume, uploads):
        has_primary = perfume.images.filter(is_primary=True).exists()
        order = perfume.images.count()
        for upload in uploads:
            PerfumeImage.objects.create(
                perfume=perfume,
                image=upload,
                alt_text=perfume.name,
                is_primary=not has_primary,
                order=order,
            )
            has_primary = True
            order += 1

    def _ensure_primary(self, perfume):
        images = list(perfume.images.all())
        if images and not any(image.is_primary for image in images):
            images[0].is_primary = True
            images[0].save(update_fields=["is_primary"])


class ContainerSerializer(serializers.ModelSerializer):
    image_url = serializers.ReadOnlyField()

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
            "price",
            "main_chords",
            "is_active",
        )


def with_last_review(queryset):
    return queryset.annotate(last_review_at=Max("reviews__created_at"))
