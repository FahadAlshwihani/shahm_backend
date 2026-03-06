from django.contrib import admin
from .models import Category, Tag, BlogPost

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_ar", "slug")
    search_fields = ("name_ar", "name_en")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name_ar", "slug")
    search_fields = ("name_ar", "name_en")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title_ar", "category", "status", "is_featured", "created_at")
    list_filter = ("status", "category", "is_featured")
    search_fields = ("title_ar", "title_en")
    prepopulated_fields = {"slug": ("title_en",)}
