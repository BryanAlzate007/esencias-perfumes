from django.contrib import admin
from django.urls import include, path, re_path

from apps.accounts.data_deletion import FacebookDataDeletionView
from apps.core.media import stored_media

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/deletedates", FacebookDataDeletionView.as_view(), name="facebook-data-deletion"),
    path("users/deletedates/", FacebookDataDeletionView.as_view(), name="facebook-data-deletion-slash"),
    path("accounts/", include("allauth.urls")),
    path("_allauth/", include("allauth.headless.urls")),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.perfumes.urls")),
    path("api/v1/", include("apps.reviews.urls")),
    path("api/v1/", include("apps.purchases.urls")),
    path("api/v1/", include("apps.payments.urls")),
    path("api/v1/", include("apps.chatia.urls")),
    path("api-auth/", include("rest_framework.urls"))

]
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", stored_media),
]
