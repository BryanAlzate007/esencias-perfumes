from rest_framework import serializers

from apps.perfumes.models import Perfume

from .models import CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    perfume_name = serializers.CharField(source="perfume.name", read_only=True)
    brand = serializers.CharField(source="perfume.brand", read_only=True)
    image_url = serializers.URLField(source="perfume.image_url", read_only=True)
    price = serializers.DecimalField(source="perfume.price", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ("id", "perfume", "perfume_name", "brand", "image_url", "price", "quantity")
        read_only_fields = ("id", "perfume_name", "brand", "image_url", "price")

    def validate_perfume(self, value):
        if not value.is_active:
            raise serializers.ValidationError("This perfume is not available.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        perfume = validated_data["perfume"]
        quantity = validated_data.get("quantity", 1)
        item, created = CartItem.objects.get_or_create(
            user=user,
            perfume=perfume,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity"])
        return item


class OrderItemSerializer(serializers.ModelSerializer):
    perfume_name = serializers.CharField(source="perfume.name", read_only=True)
    brand = serializers.CharField(source="perfume.brand", read_only=True)
    image_url = serializers.URLField(source="perfume.image_url", read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "perfume", "perfume_name", "brand", "image_url", "quantity", "unit_price", "subtotal")


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
