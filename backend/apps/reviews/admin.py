from django.contrib import admin

from .models import OccasionVote, Rating, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("perfume", "user", "created_at")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("perfume", "user", "sentiment")


@admin.register(OccasionVote)
class OccasionVoteAdmin(admin.ModelAdmin):
    list_display = ("perfume", "user", "occasion")
