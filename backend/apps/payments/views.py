from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .serializers import PaymentSessionSerializer, PaymentSyncSerializer
from .services import PaymentError, handle_event, session_payload, start_payment, sync_transaction


def _error(error):
    return Response({"detail": error.detail}, status=error.status_code)


class PaymentSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentSessionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = start_payment(request.user, serializer.validated_data.get("order"))
        except PaymentError as error:
            return _error(error)
        return Response(session_payload(payment), status=status.HTTP_201_CREATED)


class PaymentSyncView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PaymentSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment = sync_transaction(request.user, serializer.validated_data["transaction_id"])
        except PaymentError as error:
            return _error(error)
        payment.order.refresh_from_db(fields=["status"])
        return Response(
            {
                "reference": payment.reference,
                "status": payment.status,
                "order_id": payment.order_id,
                "order_status": payment.order.status,
                "amount_in_cents": payment.amount_in_cents,
            }
        )


class PaymentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, reference):
        payment = Payment.objects.filter(reference=reference, order__user=request.user).select_related("order").first()
        if payment is None:
            return Response({"detail": "Pago no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "reference": payment.reference,
                "status": payment.status,
                "order_id": payment.order_id,
                "order_status": payment.order.status,
                "amount_in_cents": payment.amount_in_cents,
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class WompiEventView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]

    def post(self, request):
        header = request.headers.get("X-Event-Checksum", "")
        try:
            handle_event(request.data, header)
        except PaymentError as error:
            return _error(error)
        return Response(status=status.HTTP_200_OK)
