from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.routers import DefaultRouter

from .views import AdminUserDetailView, AdminUserListView, CsrfCookieView, MeView, ProfilePersonViewSet

router = DefaultRouter()
router.register("profile-persons", ProfilePersonViewSet, basename="profile-person")

urlpatterns = [
    path("csrf/", ensure_csrf_cookie(CsrfCookieView.as_view()), name="csrf-cookie"),
    path("me/", MeView.as_view(), name="me"),
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    *router.urls,
]
