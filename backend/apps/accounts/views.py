from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.middleware.csrf import get_token
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdminRole
from apps.purchases.models import Order

from .models import PointsAccount, Profile_person, Referral, Reward
from .points import sync_purchase_points
from .referrals import claim_referral, ensure_referral_qr
from .serializers import AdminUserSerializer, MeSerializer, ProfilePersonSerializer, RewardSerializer

User = get_user_model()


class ProfilePersonViewSet(viewsets.ModelViewSet):
    serializer_class = ProfilePersonSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = Profile_person.objects.all()
    pagination_class = None


@method_decorator(never_cache, name="dispatch")
class CsrfCookieView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"detail": "ok", "csrfToken": get_token(request)})


class CaptchaConfigView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({
            "site_key": settings.RECAPTCHA_SITE_KEY,
            "action": settings.RECAPTCHA_ACTION,
        })


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return User.objects.select_related("profile", "points_account").get(pk=self.request.user.pk)


class PointsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sync_purchase_points(request.user)
        account = getattr(request.user, "points_account", None)
        if account is not None:
            account.refresh_from_db()
        balance = account.balance if account else 0
        has_purchase = Order.objects.filter(user=request.user, status=Order.Status.CONFIRMED).exists()
        rewards = Reward.objects.filter(active=True) if has_purchase else Reward.objects.none()
        return Response(
            {
                "points": balance,
                "has_purchase": has_purchase,
                "rewards": RewardSerializer(rewards, many=True, context={"balance": balance}).data,
            }
        )


class RedeemRewardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not Order.objects.filter(user=request.user, status=Order.Status.CONFIRMED).exists():
            return Response(
                {"detail": "Los puntos se habilitan después de la primera compra."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reward = Reward.objects.filter(pk=request.data.get("reward"), active=True).first()
        if reward is None:
            return Response({"detail": "Premio no disponible."}, status=status.HTTP_400_BAD_REQUEST)
        account = getattr(request.user, "points_account", None)
        if account is None:
            return Response(
                {"detail": "No tienes puntos suficientes para este premio."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            account.redeem(reward)
        except ValidationError as error:
            message = error.messages[0] if getattr(error, "messages", None) else "No se pudo redimir el premio."
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)
        account.refresh_from_db()
        return Response(
            {
                "points": account.balance,
                "reward": RewardSerializer(reward, context={"balance": account.balance}).data,
            }
        )


class ReferralsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sync_purchase_points(request.user)
        has_purchase = Order.objects.filter(user=request.user, status=Order.Status.CONFIRMED).exists()
        account = PointsAccount.objects.filter(user=request.user).first()
        qr_url = ""
        code = ""
        if has_purchase and account is not None:
            if not account.enabled:
                account.enable()
            account = ensure_referral_qr(account)
            code = account.referral_code
            if account.referral_qr:
                qr_url = account.referral_qr.url
        people = []
        if has_purchase:
            people = (
                Referral.objects.filter(referrer=request.user, status=Referral.Status.CREDITED)
                .select_related("referred")
                .order_by("-purchased_at", "-created_at")
            )
        return Response(
            {
                "enabled": has_purchase,
                "username": request.user.username,
                "code": code,
                "qr_url": qr_url,
                "referrals": [
                    {
                        "username": item.referred.username,
                        "purchased_at": item.purchased_at,
                    }
                    for item in people
                    if item.purchased_at is not None
                ],
            }
        )


class ClaimReferralView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            referral = claim_referral(request.user, request.data.get("code", ""))
        except ValidationError as error:
            message = error.messages[0] if getattr(error, "messages", None) else "El código de referido no es válido."
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"code": referral.code})


class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = User.objects.select_related("profile").order_by("-date_joined")


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = User.objects.select_related("profile")
