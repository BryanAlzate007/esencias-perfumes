from rest_framework import serializers

from apps.perfumes.models import Perfume

from .models import CartItem, Order, OrderItem
from .pricing import line_total


class CartItemSerializer(serializers.ModelSerializer):
    perfume_name = serializers.CharField(source="perfume.name", read_only=True)
    brand = serializers.CharField(source="perfume.brand", read_only=True)
    image_url = serializers.URLField(source="perfume.image_url", read_only=True)
    container_name = serializers.SerializerMethodField()
    price = serializers.DecimalField(source="unit_price", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = (
            "id",
            "perfume",
            "perfume_name",
            "brand",
            "image_url",
            "container",
            "container_name",
            "grams",
            "price",
            "quantity",
        )
        read_only_fields = ("id", "perfume_name", "brand", "image_url", "container_name", "price")

    def get_container_name(self, obj):
        if obj.container_id is None:
            return ""
        return obj.container.name

    def validate_perfume(self, value):
        if not value.is_active:
            raise serializers.ValidationError("This perfume is not available.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        perfume = validated_data["perfume"]
        container = validated_data.get("container")
        quantity = validated_data.get("quantity", 1)
        if container is None:
            grams = quantity
            unit_price = perfume.price
        else:
            grams, unit_price = line_total(perfume, container, validated_data.get("grams", quantity))
            quantity = 1
        item, created = CartItem.objects.get_or_create(
            user=user,
            perfume=perfume,
            container=container,
            defaults={"quantity": quantity, "grams": grams, "unit_price": unit_price},
        )
        if not created and container is None:
            item.quantity += quantity
            item.unit_price = perfume.price
            item.save(update_fields=["quantity", "unit_price", "updated_at"])
        elif not created:
            item.quantity = 1
            item.grams = grams
            item.unit_price = unit_price
            item.save(update_fields=["quantity", "grams", "unit_price", "updated_at"])
        return item


class OrderItemSerializer(serializers.ModelSerializer):
    perfume_name = serializers.CharField(source="perfume.name", read_only=True)
    brand = serializers.CharField(source="perfume.brand", read_only=True)
    image_url = serializers.URLField(source="perfume.image_url", read_only=True)
    container_name = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "perfume",
            "perfume_name",
            "brand",
            "image_url",
            "container",
            "container_name",
            "grams",
            "quantity",
            "unit_price",
            "subtotal",
        )

    def get_container_name(self, obj):
        if obj.container_id is None:
            return ""
        return obj.container.name


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Order
        fields = ("id", "username", "status", "items", "total", "created_at", "updated_at")
        read_only_fields = ("id", "username", "items", "total", "created_at", "updated_at")


class OwnedPerfumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfume
        fields = ("id", "name", "brand", "description", "notes", "image_url", "price")
