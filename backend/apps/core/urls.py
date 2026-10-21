from django.urls import path

from .views import ContactView, DashboardStatsView, HealthCheckView

urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    path("dashboard/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("contact/", ContactView.as_view(), name="contact"),
]
