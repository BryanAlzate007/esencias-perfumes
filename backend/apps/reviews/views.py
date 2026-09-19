from django.db.models import Count
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import is_admin_user
from apps.perfumes.models import Perfume

from .models import Occasion, OccasionVote, Rating, Review, Sentiment
from .serializers import OccasionVoteSerializer, RatingSerializer, ReviewSerializer


def community_payload(perfume, user):
    rating_counts = {choice: 0 for choice, _ in Sentiment.choices}
    for row in perfume.ratings.values("sentiment").annotate(total=Count("id")):
        rating_counts[row["sentiment"]] = row["total"]

    occasion_counts = {choice: 0 for choice, _ in Occasion.choices}
    for row in perfume.occasion_votes.values("occasion").annotate(total=Count("id")):
        occasion_counts[row["occasion"]] = row["total"]

    my_sentiment = None
    my_occasions = []
    if user.is_authenticated:
        rating = perfume.ratings.filter(user=user).first()
        my_sentiment = rating.sentiment if rating else None
        my_occasions = list(perfume.occasion_votes.filter(user=user).values_list("occasion", flat=True))

    return {
        "rating_counts": rating_counts,
        "occasion_counts": occasion_counts,
        "my_sentiment": my_sentiment,
        "my_occasions": my_occasions,
    }


class PerfumeReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        return Review.objects.filter(perfume_id=self.kwargs["perfume_pk"]).select_related("user", "perfume")

    def perform_create(self, serializer):
        perfume = generics.get_object_or_404(Perfume, pk=self.kwargs["perfume_pk"], is_active=True)
        serializer.save(user=self.request.user, perfume=perfume)


class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Review.objects.select_related("user", "perfume")
        if is_admin_user(self.request.user):
            return queryset
        return queryset.filter(user=self.request.user)


class ReviewDeleteView(generics.DestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Review.objects.all()

    def get_queryset(self):
        if is_admin_user(self.request.user):
            return Review.objects.all()
        return Review.objects.filter(user=self.request.user)


class PerfumeCommunityView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, perfume_pk):
        perfume = generics.get_object_or_404(Perfume, pk=perfume_pk)
        return Response(community_payload(perfume, request.user))


class PerfumeRatingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, perfume_pk):
        perfume = generics.get_object_or_404(Perfume, pk=perfume_pk, is_active=True)
        serializer = RatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Rating.objects.update_or_create(
            perfume=perfume,
            user=request.user,
            defaults={"sentiment": serializer.validated_data["sentiment"]},
        )
        return Response(community_payload(perfume, request.user))


class PerfumeOccasionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, perfume_pk):
        perfume = generics.get_object_or_404(Perfume, pk=perfume_pk, is_active=True)
        serializer = OccasionVoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        occasion = serializer.validated_data["occasion"]
        selected = serializer.validated_data["selected"]
        if selected:
            OccasionVote.objects.get_or_create(perfume=perfume, user=request.user, occasion=occasion)
        else:
            OccasionVote.objects.filter(perfume=perfume, user=request.user, occasion=occasion).delete()
        return Response(community_payload(perfume, request.user))
