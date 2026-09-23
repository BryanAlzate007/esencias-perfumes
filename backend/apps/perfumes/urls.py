from rest_framework.routers import DefaultRouter

from .views import ContainerViewSet, MainChordViewSet, PerfumeViewSet

router = DefaultRouter()
router.register("perfumes", PerfumeViewSet, basename="perfume")
router.register("main-chords", MainChordViewSet, basename="main-chord")
router.register("containers", ContainerViewSet, basename="container")

urlpatterns = router.urls
