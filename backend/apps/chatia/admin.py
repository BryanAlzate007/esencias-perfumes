from django.contrib import admin

from .models import ChatIA, Message, OlfactoryTest, PerfumeOlfactoryProfile


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "content", "created_at")
    can_delete = False


@admin.register(ChatIA)
class ChatIAAdmin(admin.ModelAdmin):
    list_display = ("advisor_name", "email", "language", "created_at")
    search_fields = ("email", "advisor_name", "public_id")
    readonly_fields = ("public_id", "created_at", "updated_at")
    inlines = [MessageInline]


@admin.register(OlfactoryTest)
class OlfactoryTestAdmin(admin.ModelAdmin):
    list_display = ("email", "primary_family", "status", "completed_at", "created_at")
    list_filter = ("status", "primary_family")
    search_fields = ("email",)
    readonly_fields = (
        "answers",
        "scores",
        "created_at",
        "updated_at",
        "completed_at",
        "email_sent_at",
    )


@admin.register(PerfumeOlfactoryProfile)
class PerfumeOlfactoryProfileAdmin(admin.ModelAdmin):
    list_display = ("email", "primary_family", "floral_score", "citrus_score", "oriental_score", "woody_score", "updated_at")
    search_fields = ("email",)
    readonly_fields = ("created_at", "updated_at")
