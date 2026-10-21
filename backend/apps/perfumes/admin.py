from django.contrib import admin

from .models import Perfume, PerfumeContainerPrice


class PerfumeContainerPriceInline(admin.TabularInline):
    model = PerfumeContainerPrice
    extra = 1


@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "price", "is_active")
    search_fields = ("name", "brand")
    inlines = [PerfumeContainerPriceInline]


@admin.register(PerfumeContainerPrice)
class PerfumeContainerPriceAdmin(admin.ModelAdmin):
    list_display = ("perfume", "container", "price", "price_usd")
    list_filter = ("container",)
    search_fields = ("perfume__name", "perfume__brand", "container__name")
