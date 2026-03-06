from django.contrib import admin
from .models import HeroSection, HeroMedia, FooterColumn, FooterLink, Page


# ===========================
# HERO SECTION ADMIN
# ===========================
@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "is_active", "order")
    list_editable = ("is_active", "order")
    search_fields = ("slug",)
    ordering = ("order",)


# ===========================
# HERO MEDIA ADMIN
# ===========================
@admin.register(HeroMedia)
class HeroMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "hero", "media_type", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("hero__slug",)
    ordering = ("order",)


# ===========================
# FOOTER
# ===========================
class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1


@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
    list_display = ("title_ar", "order", "is_active")
    list_editable = ("order", "is_active")
    inlines = [FooterLinkInline]
    ordering = ("order",)


# ===========================
# PAGES
# ===========================
@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("slug", "title_ar", "is_published", "show_in_sitemap", "updated_at")
    list_editable = ("is_published", "show_in_sitemap")
    search_fields = ("slug", "title_ar", "title_en")
    ordering = ("slug",)
