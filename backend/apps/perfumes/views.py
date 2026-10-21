from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from apps.core.permissions import IsAdminRole, is_admin_user

from .excel import ExcelImportError, export_perfumes_workbook, import_perfumes_workbook
from .models import Container, Main_chords, Perfume
from .serializers import (
    ContainerSerializer,
    MainChordSerializer,
    PerfumeSerializer,
    PerfumeWriteSerializer,
    with_last_review,
)


class PerfumePagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100


class AdminCatalogViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    pagination_class = None


class MainChordViewSet(AdminCatalogViewSet):
    serializer_class = MainChordSerializer
    queryset = Main_chords.objects.all()


class PerfumeViewSet(viewsets.ModelViewSet):
    pagination_class = PerfumePagination

    def get_queryset(self):
        queryset = with_last_review(Perfume.objects.prefetch_related("main_chords", "images")).order_by("name")
        if self.action in ("list", "retrieve") and not is_admin_user(self.request.user):
            queryset = queryset.filter(is_active=True)
        if self.action == "list":
            queryset = self._filter_list(queryset)
        return queryset

    def paginate_queryset(self, queryset):
        if self.action == "list" and self._list_is_filtered():
            return None
        return super().paginate_queryset(queryset)

    def _list_is_filtered(self):
        params = self.request.query_params
        return bool(params.get("catalog", "").strip() or params.get("search", "").strip())

    def _filter_list(self, queryset):
        catalog = self.request.query_params.get("catalog", "").strip().lower()
        search = self.request.query_params.get("search", "").strip()
        if catalog:
            allowed = {choice.value for choice in Perfume.Catalog}
            queryset = queryset.filter(catalog=catalog) if catalog in allowed else queryset.none()
        if search:
            queryset = queryset.filter(name__icontains=search[:80])
        return queryset

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return PerfumeWriteSerializer
        return PerfumeSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminRole()]

    @action(detail=False, methods=["get"], url_path="export")
    def export_excel(self, request):
        return export_perfumes_workbook(self.get_queryset())

    @action(detail=False, methods=["post"], url_path="import")
    def import_excel(self, request):
        upload = request.FILES.get("file")
        if upload is None:
            return Response({"detail": "Adjunta un archivo de Excel."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = import_perfumes_workbook(upload)
        except ExcelImportError as exc:
            return Response({"detail": exc.detail, "errors": exc.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)


class ContainerViewSet(AdminCatalogViewSet):
    serializer_class = ContainerSerializer
    queryset = Container.objects.prefetch_related("main_chords", "images")
