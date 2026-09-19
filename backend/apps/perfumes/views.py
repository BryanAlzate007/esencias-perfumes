from rest_framework import permissions, viewsets

from apps.core.permissions import IsAdminRole, is_admin_user

from .models import Perfume
from .serializers import PerfumeSerializer, PerfumeWriteSerializer, with_last_review


class PerfumeViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = with_last_review(Perfume.objects.all()).order_by("name")
        if self.action in ("list", "retrieve") and not is_admin_user(self.request.user):
            queryset = queryset.filter(is_active=True)
        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PerfumeWriteSerializer
        return PerfumeSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminRole()]
