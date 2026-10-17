import base64
import hashlib
import hmac
import json
import logging
import secrets
from urllib.parse import urlencode

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.chatia.models import ChatIA
from apps.payments.models import Payment
from apps.purchases.models import Order

from .models import DataDeletionRequest, Profile

logger = logging.getLogger(__name__)


class InvalidSignedRequest(Exception):
    pass


def _decode(value):
    padded = value + "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(padded.encode("ascii"))


def parse_signed_request(signed_request, secret):
    if not signed_request or "." not in signed_request or not secret:
        raise InvalidSignedRequest
    encoded_sig, payload = signed_request.split(".", 1)
    try:
        signature = _decode(encoded_sig)
        data = json.loads(_decode(payload))
    except (ValueError, json.JSONDecodeError, UnicodeError) as error:
        raise InvalidSignedRequest from error
    expected = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise InvalidSignedRequest
    if str(data.get("algorithm", "")).upper() != "HMAC-SHA256":
        raise InvalidSignedRequest
    user_id = data.get("user_id")
    if user_id in (None, ""):
        raise InvalidSignedRequest
    return str(user_id)


def _clear_profile(user):
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        return
    profile.phone = ""
    profile.whatsapp = ""
    profile.country = ""
    profile.preferred_language = ""
    profile.save(update_fields=["phone", "whatsapp", "country", "preferred_language"])


def _is_privileged(user):
    if user.is_staff or user.is_superuser:
        return True
    try:
        return user.profile.role == Profile.Role.ADMIN
    except Profile.DoesNotExist:
        return False


def erase_linked_user(user):
    if _is_privileged(user):
        return DataDeletionRequest.Status.KEPT

    user.cart_items.all().delete()
    user.reviews.all().delete()
    user.ratings.all().delete()
    user.occasion_votes.all().delete()
    ChatIA.objects.filter(user=user).delete()

    orders = Order.objects.filter(user=user)
    Payment.objects.filter(order__in=orders).exclude(status=Payment.Status.APPROVED).delete()
    orders.exclude(payments__status=Payment.Status.APPROVED).delete()
    Payment.objects.filter(order__user=user).update(customer_email="")

    SocialAccount.objects.filter(user=user).delete()
    EmailAddress.objects.filter(user=user).delete()
    _clear_profile(user)

    user.username = f"deleted-{user.pk}"
    user.email = ""
    user.first_name = ""
    user.last_name = ""
    user.is_active = False
    user.set_unusable_password()
    user.save(
        update_fields=[
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "password",
        ]
    )
    return DataDeletionRequest.Status.DELETED


def handle_deletion(facebook_user_id):
    account = (
        SocialAccount.objects.filter(provider="facebook", uid=facebook_user_id)
        .select_related("user", "user__profile")
        .first()
    )
    if account is None:
        outcome = DataDeletionRequest.Status.ABSENT
    else:
        outcome = erase_linked_user(account.user)
    return DataDeletionRequest.objects.create(
        confirmation_code=secrets.token_hex(16),
        facebook_user_id=facebook_user_id,
        status=outcome,
    )


def _page(title, body, code=""):
    code_line = f"<p>Código: <strong>{escape(code)}</strong></p>" if code else ""
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 36rem; margin: 4rem auto; padding: 0 1.25rem; line-height: 1.5; color: #1c1917; }}
    h1 {{ font-size: 1.5rem; }}
  </style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <p>{body}</p>
  {code_line}
</body>
</html>"""
    return HttpResponse(html)


def status_page(code):
    if not code:
        return _page(
            "Eliminación de datos",
            "Facebook envía aquí la solicitud de eliminación. Con el código de confirmación puedes ver el estado.",
        )
    request = DataDeletionRequest.objects.filter(confirmation_code=code).first()
    if request is None:
        return _page("Eliminación de datos", "No encontramos una solicitud con ese código.")
    messages = {
        DataDeletionRequest.Status.DELETED: (
            "Eliminamos la cuenta asociada a Facebook: perfil, carrito, opiniones y conversaciones. "
            "Si hubo una venta, conservamos el soporte que exige la ley, sin nombre ni correo."
        ),
        DataDeletionRequest.Status.ABSENT: "No había datos asociados a esa cuenta de Facebook.",
        DataDeletionRequest.Status.KEPT: (
            "Recibimos la solicitud. Esa cuenta es de administración y no se elimina por este aviso."
        ),
    }
    return _page("Eliminación de datos", messages[request.status], request.confirmation_code)


@method_decorator(csrf_exempt, name="dispatch")
class FacebookDataDeletionView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    parser_classes = [FormParser, MultiPartParser]

    def get(self, request):
        return status_page(request.query_params.get("code", "").strip())

    def post(self, request):
        secret = settings.FACEBOOK_CLIENT_SECRET
        if not secret:
            return Response(
                {"detail": "Facebook no está configurado."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        try:
            facebook_user_id = parse_signed_request(request.data.get("signed_request", ""), secret)
        except InvalidSignedRequest:
            return Response({"detail": "Solicitud inválida."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            deletion = handle_deletion(facebook_user_id)
        logger.info(
            "Facebook data deletion %s for user %s",
            deletion.status,
            facebook_user_id,
        )
        status_url = request.build_absolute_uri("/users/deletedates")
        status_url = f"{status_url}?{urlencode({'code': deletion.confirmation_code})}"
        return Response(
            {"url": status_url, "confirmation_code": deletion.confirmation_code}
        )
