import json
from decimal import Decimal, InvalidOperation

from django.db.models import Max
from rest_framework import serializers

from apps.core.permissions import is_admin_user

from .models import Container, EnvaseImage, Main_chords, Perfume, PerfumeContainerPrice, PerfumeImage

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


def _parse_money(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise serializers.ValidationError("Precio inválido.") from exc
    if amount < 0 or amount.as_tuple().exponent < -2:
        raise serializers.ValidationError("Precio inválido.")
    return amount.quantize(Decimal("0.01"))


class ContainerPriceField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, str):
            data = json.loads(data) if data else []
        if not isinstance(data, list):
            raise serializers.ValidationError("Se esperaba una lista de precios por envase.")
        rows = []
        for item in data:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Precio de envase inválido.")
            try:
                container_id = int(item.get("container"))
            except (TypeError, ValueError) as exc:
                raise serializers.ValidationError("Envase inválido.") from exc
            price = item.get("price")
            price_usd = item.get("price_usd")
            if price in ("", None) and price_usd in ("", None):
                continue
            if price in ("", None):
                raise serializers.ValidationError("El precio en pesos es obligatorio.")
            rows.append(
                {
                    "container_id": container_id,
                    "price": _parse_money(price),
                    "price_usd": None if price_usd in ("", None) else _parse_money(price_usd),
                }
            )
        ids = [row["container_id"] for row in rows]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Envase repetido.")
        found = set(Container.objects.filter(id__in=ids).values_list("id", flat=True))
        if found != set(ids):
            raise serializers.ValidationError("Envase no encontrado.")
        return rows

    def to_representation(self, value):
        stored = value.all() if hasattr(value, "all") else value
        return [
            {
                "container": item.container_id,
                "price": format(item.price, ".2f"),
                "price_usd": None if item.price_usd is None else format(item.price_usd, ".2f"),
            }
            for item in stored
        ]


class PerfumeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfumeImage
        fields = ("id", "image", "alt_text", "is_primary", "order")
        read_only_fields = fields


class PerfumeSerializer(serializers.ModelSerializer):
    images = PerfumeImageSerializer(many=True, read_only=True)
    image_url = serializers.ReadOnlyField()
    last_review_at = serializers.DateTimeField(read_only=True, allow_null=True)
    container_prices = ContainerPriceField(read_only=True)

    class Meta:
        model = Perfume
        fields = (*PERFUME_FIELDS, "images", "image_url", "container_prices", "last_review_at", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at", "last_review_at", "image_url", "container_prices")

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if not is_admin_user(getattr(request, "user", None)):
            fields.pop("container_prices", None)
        return fields


class PerfumeWriteSerializer(serializers.ModelSerializer):
    price_usd = OptionalDecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    is_active = ExplicitBooleanField(required=False)
    main_chords = MainChordField(required=False)
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    remove_image_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    container_prices = ContainerPriceField(required=False)

    class Meta:
        model = Perfume
        fields = (*PERFUME_FIELDS, "images", "remove_image_ids", "container_prices")

    def create(self, validated_data):
        uploads = validated_data.pop("images", [])
        validated_data.pop("remove_image_ids", None)
        prices = validated_data.pop("container_prices", [])
        perfume = super().create(validated_data)
        self._store_images(perfume, uploads)
        self._store_container_prices(perfume, prices)
        return perfume

    def update(self, instance, validated_data):
        uploads = validated_data.pop("images", [])
        remove_ids = validated_data.pop("remove_image_ids", [])
        prices = validated_data.pop("container_prices", None)
        perfume = super().update(instance, validated_data)
        if remove_ids:
            for image in perfume.images.filter(id__in=remove_ids):
                image.image.delete(save=False)
                image.delete()
        self._store_images(perfume, uploads)
        self._ensure_primary(perfume)
        if prices is not None:
            self._store_container_prices(perfume, prices)
        return perfume

    def _store_container_prices(self, perfume, rows):
        kept = []
        for row in rows:
            price, _created = PerfumeContainerPrice.objects.update_or_create(
                perfume=perfume,
                container_id=row["container_id"],
                defaults={"price": row["price"], "price_usd": row["price_usd"]},
            )
            kept.append(price.id)
        perfume.container_prices.exclude(id__in=kept).delete()

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
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Container
        fields = (
            "id",
            "name",
            "description",
            "image_url",
            "image",
            "type",
            "size",
            "weight",
            "volume",
            "material",
            "color",
            "price",
            "is_active",
        )

    def create(self, validated_data):
        upload = validated_data.pop("image", None)
        container = super().create(validated_data)
        self._store_image(container, upload)
        return container

    def update(self, instance, validated_data):
        upload = validated_data.pop("image", None)
        container = super().update(instance, validated_data)
        self._store_image(container, upload)
        return container

    def _store_image(self, container, upload):
        if not upload:
            return
        for stored in list(container.images.all()):
            stored.delete()
        EnvaseImage.objects.create(
            container=container,
            image=upload,
            alt_text=container.name,
            is_primary=True,
            order=0,
        )


def with_last_review(queryset):
    return queryset.annotate(last_review_at=Max("reviews__created_at"))
