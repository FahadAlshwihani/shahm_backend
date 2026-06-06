from django.contrib import admin
from .models import (
    Category,
    Tag,
    BlogPost,
    BlogSection,
    BlogPageSettings,
)


# =========================
# Blog Sections Inline
# =========================
class BlogSectionInline(admin.TabularInline):
    model = BlogSection
    extra = 0
    ordering = ("order",)


# =========================
# Categories
# =========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name_ar",
        "name_en",
        "slug",
        "color",
    )

    search_fields = (
        "name_ar",
        "name_en",
        "slug",
    )

    list_filter = (
        "color",
    )

    ordering = ("name_ar",)


# =========================
# Tags
# =========================
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name_ar",
        "name_en",
        "slug",
    )

    search_fields = (
        "name_ar",
        "name_en",
        "slug",
    )

    ordering = ("name_ar",)


# =========================
# Blog Posts
# =========================
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    inlines = [BlogSectionInline]

    list_display = (
        "id",
        "title_ar",
        "category",
        "author",
        "status",
        "is_featured",
        "views_count",
        "publish_date",
        "created_at",
    )

    list_filter = (
        "status",
        "category",
        "is_featured",
        "created_at",
        "publish_date",
    )

    search_fields = (
        "title_ar",
        "title_en",
        "slug",
        "intro_ar",
        "intro_en",
    )

    readonly_fields = (
        "views_count",
        "created_at",
        "updated_at",
        "read_time",
    )

    filter_horizontal = (
        "tags",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "title_ar",
                    "title_en",
                    "slug",
                    "author",
                    "category",
                    "tags",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "intro_ar",
                    "intro_en",
                )
            },
        ),
        (
            "Images",
            {
                "fields": (
                    "cover_image",
                    "image",
                )
            },
        ),
        (
            "Publishing",
            {
                "fields": (
                    "status",
                    "publish_date",
                    "is_featured",
                )
            },
        ),
        (
            "SEO",
            {
                "fields": (
                    "seo_title",
                    "seo_description",
                )
            },
        ),
        (
            "Statistics",
            {
                "fields": (
                    "views_count",
                    "read_time",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


# =========================
# Sections
# =========================
@admin.register(BlogSection)
class BlogSectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "post",
        "title_ar",
        "order",
    )

    list_filter = (
        "post",
    )

    search_fields = (
        "title_ar",
        "title_en",
    )

    ordering = (
        "post",
        "order",
    )


# =========================
# Blog Settings
# =========================
@admin.register(BlogPageSettings)
class BlogPageSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "page_title_ar",
        "page_title_en",
        "updated_at",
    )

    readonly_fields = (
        "updated_at",
    )