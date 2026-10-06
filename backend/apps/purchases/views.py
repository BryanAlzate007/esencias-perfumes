from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminRole, is_admin_user
from apps.perfumes.models import Container, Perfume

from .models import CartItem, Order, OrderItem
from .pricing import build_quote, line_total
from .serializers import CartItemSerializer, OrderSerializer, OwnedPerfumeSerializer


class CartListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related("perfume", "container")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related("perfume", "container")


def _draft_item(user, pk):
    order = (
        Order.objects.filter(pk=pk, user=user, status=Order.Status.DRAFT)
        .prefetch_related("items__perfume", "items__container")
        .first()
    )
    if order is None:
        return None
    return order.items.select_related("perfume", "container").first()


class DraftOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        perfume = Perfume.objects.filter(pk=request.data.get("perfume"), is_active=True).first()
        if perfume is None:
            return Response({"detail": "Perfume no disponible."}, status=status.HTTP_400_BAD_REQUEST)
        grams, total = line_total(perfume, None, perfume.grams)
        order = Order.objects.create(user=request.user, status=Order.Status.DRAFT)
        item = OrderItem.objects.create(
            order=order,
            perfume=perfume,
            quantity=1,
            grams=grams,
            unit_price=total,
        )
        return Response(build_quote(item), status=status.HTTP_201_CREATED)


class QuoteOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        item = _draft_item(request.user, pk)
        if item is None:
            return Response({"detail": "Pedido no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        container = item.container
        if "container" in request.data:
            raw_container = request.data.get("container")
            if raw_container in (None, ""):
                container = None
            else:
                container = Container.objects.filter(pk=raw_container, is_active=True).first()
                if container is None:
                    return Response({"container": ["Envase no disponible."]}, status=status.HTTP_400_BAD_REQUEST)
        grams, total = line_total(item.perfume, container, request.data.get("grams", item.grams))
        item.container = container
        item.grams = grams
        item.unit_price = total
        item.save(update_fields=["container", "grams", "unit_price"])
        return Response(build_quote(item))


class ConfirmDraftView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        item = _draft_item(request.user, pk)
        if item is None:
            return Response({"detail": "Pedido no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        cart, created = CartItem.objects.get_or_create(
            user=request.user,
            perfume=item.perfume,
            container=item.container,
            defaults={"quantity": 1, "grams": item.grams, "unit_price": item.unit_price},
        )
        if not created:
            cart.quantity = 1
            cart.grams = item.grams
            cart.unit_price = item.unit_price
            cart.save(update_fields=["quantity", "grams", "unit_price", "updated_at"])
        item.order.delete()
        return Response(CartItemSerializer(cart).data, status=status.HTTP_201_CREATED)


class DiscardDraftView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        Order.objects.filter(pk=pk, user=request.user, status=Order.Status.DRAFT).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        items = list(CartItem.objects.filter(user=request.user).select_related("perfume", "container"))
        if not items:
            return Response({"detail": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, status=Order.Status.CONFIRMED)
        for item in items:
            OrderItem.objects.create(
                order=order,
                perfume=item.perfume,
                container=item.container,
                quantity=item.quantity,
                grams=item.grams,
                unit_price=item.unit_price if item.container_id else item.perfume.price,
            )
        CartItem.objects.filter(user=request.user).delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related("items__perfume", "items__container").select_related("user")
        queryset = queryset.exclude(status=Order.Status.DRAFT)
        if is_admin_user(self.request.user):
            return queryset
        return queryset.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.prefetch_related("items__perfume", "items__container").select_related("user")
        queryset = queryset.exclude(status=Order.Status.DRAFT)
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
            .exclude(order__status__in=[Order.Status.CANCELLED, Order.Status.DRAFT])
            .values_list("perfume_id", flat=True)
            .distinct()
        )
        return Perfume.objects.filter(id__in=perfume_ids)
