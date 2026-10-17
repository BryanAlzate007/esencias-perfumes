from django.urls import path

from .views import PaymentDetailView, PaymentSessionView, PaymentSyncView, WompiEventView

urlpatterns = [
    path("payments/", PaymentSessionView.as_view(), name="payment-session"),
    path("payments/sync/", PaymentSyncView.as_view(), name="payment-sync"),
    path("payments/wompi/events/", WompiEventView.as_view(), name="wompi-events"),
    path("payments/<str:reference>/", PaymentDetailView.as_view(), name="payment-detail"),
]
