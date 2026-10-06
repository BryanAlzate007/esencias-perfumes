from django.urls import path

from .views import (
    CartItemDetailView,
    CartListCreateView,
    CheckoutView,
    ConfirmDraftView,
    DiscardDraftView,
    DraftOrderView,
    MyPerfumesView,
    OrderDetailView,
    OrderListView,
    QuoteOrderView,
)

urlpatterns = [
    path("cart/", CartListCreateView.as_view(), name="cart"),
    path("cart/<int:pk>/", CartItemDetailView.as_view(), name="cart-item"),
    path("orders/", OrderListView.as_view(), name="orders"),
    path("orders/checkout/", CheckoutView.as_view(), name="checkout"),
    path("orders/draft/", DraftOrderView.as_view(), name="order-draft"),
    path("orders/<int:pk>/quote/", QuoteOrderView.as_view(), name="order-quote"),
    path("orders/<int:pk>/confirm/", ConfirmDraftView.as_view(), name="order-confirm"),
    path("orders/<int:pk>/draft/", DiscardDraftView.as_view(), name="order-draft-discard"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("my-perfumes/", MyPerfumesView.as_view(), name="my-perfumes"),
]
