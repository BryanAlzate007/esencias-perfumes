from django.urls import path

from .views import (
    CartItemDetailView,
    CartListCreateView,
    CheckoutView,
    MyPerfumesView,
    OrderDetailView,
    OrderListView,
)

urlpatterns = [
    path("cart/", CartListCreateView.as_view(), name="cart"),
    path("cart/<int:pk>/", CartItemDetailView.as_view(), name="cart-item"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("orders/checkout/", CheckoutView.as_view(), name="checkout"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("my-perfumes/", MyPerfumesView.as_view(), name="my-perfumes"),
]
