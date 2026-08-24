from django.contrib import admin
from .models import LegalPage, LegalSection, LegalSubSection


class LegalSectionInline(admin.TabularInline):
    model = LegalSection
    extra = 1
    fields = ("title_ar", "title_en", "anchor", "order")
    ordering = ("order",)


class LegalSubSectionInline(admin.TabularInline):
    model = LegalSubSection
    extra = 1
    fields = ("title_ar", "title_en", "content_ar", "content_en", "order")
    ordering = ("order",)


@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = (
        "slug",
        "title_ar",
        "title_en",
        "is_published",
        "show_in_footer",
        "order",
        "updated_at",
    )
    list_editable = ("is_published", "show_in_footer", "order")
    search_fields = ("slug", "title_ar", "title_en")
    list_filter = ("is_published", "show_in_footer")
    ordering = ("order",)
    inlines = [LegalSectionInline]


@admin.register(LegalSection)
class LegalSectionAdmin(admin.ModelAdmin):
    list_display = ("page", "title_ar", "title_en", "anchor", "order")
    list_editable = ("order",)
    search_fields = ("title_ar", "title_en", "anchor", "page__slug")
    list_filter = ("page",)
    ordering = ("page", "order")
    inlines = [LegalSubSectionInline]


@admin.register(LegalSubSection)
class LegalSubSectionAdmin(admin.ModelAdmin):
    list_display = ("section", "title_ar", "title_en", "order")
    list_editable = ("order",)
    search_fields = ("title_ar", "title_en", "section__title_ar", "section__title_en")
    list_filter = ("section__page",)
    ordering = ("section", "order")