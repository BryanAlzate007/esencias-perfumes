from rest_framework.routers import DefaultRouter

from .views import PerfumeViewSet

router = DefaultRouter()
router.register("perfumes", PerfumeViewSet, basename="perfume")

urlpatterns = router.urls
