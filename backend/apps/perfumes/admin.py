from django.contrib import admin

from .models import Perfume


@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "price", "is_active")
    search_fields = ("name", "brand")
