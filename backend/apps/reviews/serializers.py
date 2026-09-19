from rest_framework import serializers

from .models import Occasion, OccasionVote, Rating, Review, Sentiment


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    perfume_name = serializers.CharField(source="perfume.name", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "perfume", "perfume_name", "username", "body", "created_at", "updated_at")
        read_only_fields = ("id", "perfume", "perfume_name", "username", "created_at", "updated_at")


class RatingSerializer(serializers.Serializer):
    sentiment = serializers.ChoiceField(choices=Sentiment.choices)


class OccasionVoteSerializer(serializers.Serializer):
    occasion = serializers.ChoiceField(choices=Occasion.choices)
    selected = serializers.BooleanField(default=True)


class CommunityStatsSerializer(serializers.Serializer):
    rating_counts = serializers.DictField()
    occasion_counts = serializers.DictField()
    my_sentiment = serializers.CharField(allow_null=True)
    my_occasions = serializers.ListField(child=serializers.CharField())
