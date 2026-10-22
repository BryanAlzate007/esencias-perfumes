from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone

from .models import (
    DataDeletionRequest,
    PointEntry,
    PointEntryEvent,
    PointRedemption,
    PointsAccount,
    Profile,
    Referral,
    ReferralEvent,
)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(DjangoUserAdmin):
    inlines = [ProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "country", "phone", "whatsapp")
    list_filter = ("role",)


@admin.register(DataDeletionRequest)
class DataDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ("confirmation_code", "status", "facebook_user_id", "created_at")
    list_filter = ("status",)
    search_fields = ("confirmation_code", "facebook_user_id")
    readonly_fields = ("confirmation_code", "facebook_user_id", "status", "created_at")


class _HistoryInline(admin.TabularInline):
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class PointEntryEventInline(_HistoryInline):
    model = PointEntryEvent
    fields = ("status", "created_at")
    readonly_fields = ("status", "created_at")


class PointEntryInline(_HistoryInline):
    model = PointEntry
    fields = ("source", "points", "status", "order", "referral", "created_at", "redeemed_at", "redemption")
    readonly_fields = fields
    show_change_link = True


class RedeemedEntryInline(_HistoryInline):
    model = PointEntry
    fk_name = "redemption"
    fields = ("account", "source", "points", "order", "referral", "created_at", "redeemed_at")
    readonly_fields = fields
    show_change_link = True
    verbose_name_plural = "Puntos incluidos en la redención"


class ReferralEventInline(_HistoryInline):
    model = ReferralEvent
    fields = ("status", "created_at")
    readonly_fields = ("status", "created_at")


@admin.register(PointsAccount)
class PointsAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "enabled", "referral_code", "enabled_at")
    list_filter = ("enabled",)
    search_fields = ("user__username", "user__email", "referral_code")
    readonly_fields = ("balance", "referral_code", "enabled_at", "created_at", "updated_at")
    inlines = [PointEntryInline]

    def save_model(self, request, obj, form, change):
        if obj.enabled and obj.enabled_at is None:
            obj.enabled_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(PointEntry)
class PointEntryAdmin(admin.ModelAdmin):
    list_display = ("account", "source", "points", "status", "created_at", "redeemed_at")
    list_filter = ("source", "status")
    search_fields = ("account__user__username", "account__referral_code")
    readonly_fields = (
        "account",
        "source",
        "points",
        "status",
        "order",
        "referral",
        "redemption",
        "redeemed_at",
        "created_at",
    )
    inlines = [PointEntryEventInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PointRedemption)
class PointRedemptionAdmin(admin.ModelAdmin):
    list_display = ("account", "points", "created_at")
    search_fields = ("account__user__username", "account__referral_code")
    readonly_fields = ("account", "points", "created_at")
    inlines = [RedeemedEntryInline]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referred", "code", "status", "points_awarded", "created_at")
    list_filter = ("status",)
    search_fields = ("referrer__username", "referred__username", "code")
    readonly_fields = ("code", "status", "points_awarded", "created_at", "updated_at")
    inlines = [ReferralEventInline]
