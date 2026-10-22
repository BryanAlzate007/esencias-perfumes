from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.routers import DefaultRouter

from .views import (
    AdminUserDetailView,
    AdminUserListView,
    CaptchaConfigView,
    CsrfCookieView,
    MeView,
    ClaimReferralView,
    PointsView,
    ProfilePersonViewSet,
    RedeemRewardView,
    ReferralsView,
)

router = DefaultRouter()
router.register("profile-persons", ProfilePersonViewSet, basename="profile-person")

urlpatterns = [
    path("csrf/", ensure_csrf_cookie(CsrfCookieView.as_view()), name="csrf-cookie"),
    path("captcha/", CaptchaConfigView.as_view(), name="captcha-config"),
    path("me/", MeView.as_view(), name="me"),
    path("points/", PointsView.as_view(), name="points"),
    path("points/redeem/", RedeemRewardView.as_view(), name="points-redeem"),
    path("referrals/", ReferralsView.as_view(), name="referrals"),
    path("referrals/claim/", ClaimReferralView.as_view(), name="referrals-claim"),
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    *router.urls,
]
