from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminRole, is_admin_user
from apps.perfumes.models import Perfume

from .models import CartItem, Order, OrderItem
from .serializers import CartItemSerializer, OrderSerializer, OwnedPerfumeSerializer


class CartListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related("perfume")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        items = list(CartItem.objects.filter(user=request.user).select_related("perfume"))
        if not items:
            return Response({"detail": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, status=Order.Status.CONFIRMED)
        for item in items:
            OrderItem.objects.create(
                order=order,
                perfume=item.perfume,
                quantity=item.quantity,
                unit_price=item.perfume.price,
            )
        CartItem.objects.filter(user=request.user).delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related("items__perfume").select_related("user")
        if is_admin_user(self.request.user):
            return queryset
        return queryset.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related("items__perfume").select_related("user")
        if is_admin_user(self.request.user):
            return queryset
        return queryset.filter(user=self.request.user)

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH"):
            return [permissions.IsAuthenticated(), IsAdminRole()]
        return [permissions.IsAuthenticated()]


class MyPerfumesView(generics.ListAPIView):
    serializer_class = OwnedPerfumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        perfume_ids = (
            OrderItem.objects.filter(order__user=self.request.user)
            .exclude(order__status=Order.Status.CANCELLED)
            .values_list("perfume_id", flat=True)
            .distinct()
        )
        return Perfume.objects.filter(id__in=perfume_ids)
