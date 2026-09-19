from django.urls import path
from django.views.decorators.csrf import ensure_csrf_cookie

from .views import AdminUserDetailView, AdminUserListView, CsrfCookieView, MeView

urlpatterns = [
    path("csrf/", ensure_csrf_cookie(CsrfCookieView.as_view()), name="csrf-cookie"),
    path("me/", MeView.as_view(), name="me"),
    path("users/", AdminUserListView.as_view(), name="admin-users"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
]
