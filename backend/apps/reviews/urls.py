from django.urls import path

from .views import (
    PerfumeCommunityView,
    PerfumeOccasionView,
    PerfumeRatingView,
    PerfumeReviewListCreateView,
    ReviewDeleteView,
    ReviewListView,
)

urlpatterns = [
    path("reviews/", ReviewListView.as_view(), name="review-list"),
    path("reviews/<int:pk>/", ReviewDeleteView.as_view(), name="review-delete"),
    path("perfumes/<int:perfume_pk>/reviews/", PerfumeReviewListCreateView.as_view(), name="perfume-reviews"),
    path("perfumes/<int:perfume_pk>/community/", PerfumeCommunityView.as_view(), name="perfume-community"),
    path("perfumes/<int:perfume_pk>/rating/", PerfumeRatingView.as_view(), name="perfume-rating"),
    path("perfumes/<int:perfume_pk>/occasions/", PerfumeOccasionView.as_view(), name="perfume-occasions"),
]
