from django.contrib import admin
from .models import DefaultSEO, PageSEO


@admin.register(DefaultSEO)
class DefaultSEOAdmin(admin.ModelAdmin):
    list_display = ("site_title", "canonical_base", "updated_at")


@admin.register(PageSEO)
class PageSEOAdmin(admin.ModelAdmin):
    list_display = ("slug", "meta_title", "updated_at")
    search_fields = ("slug", "meta_title")
