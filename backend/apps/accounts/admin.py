from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from .models import DataDeletionRequest, Profile


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
