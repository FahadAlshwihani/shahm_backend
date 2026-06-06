from django.db import models
from django.conf import settings
from django.utils.html import strip_tags
import math


class Category(models.Model):
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)

    slug = models.SlugField(unique=True, blank=True, null=True)

    # ✅ لون الفئة
    color = models.CharField(
        max_length=7,
        default="#353C3C",
        help_text="Hex color like #FF5733"
    )

    # ✅ أيقونة الفئة (اختياري)
    icon = models.ImageField(
        upload_to="blog/category_icons/",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name_ar


class Tag(models.Model):
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name_ar


class BlogPost(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("scheduled", "Scheduled"),
    )

    title_ar = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, null=True, blank=True)

    cover_image = models.ImageField(upload_to="blog/covers/", blank=True, null=True)
    image = models.ImageField(upload_to="blog/images/", blank=True, null=True)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="posts"
    )

    tags = models.ManyToManyField(Tag, blank=True)

    # ✅ intro بدل content
    intro_ar = models.TextField(blank=True)
    intro_en = models.TextField(blank=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft"
    )

    publish_date = models.DateTimeField(blank=True, null=True)

    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="blog_posts"
    )

    views_count = models.PositiveIntegerField(default=0)

    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title_ar

    @property
    def read_time(self):
        text = strip_tags(self.intro_en or self.intro_ar or "")
        words = len(text.split())
        return max(1, math.ceil(words / 200))


class BlogSection(models.Model):
    post = models.ForeignKey(
        BlogPost,
        related_name="sections",
        on_delete=models.CASCADE
    )

    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)

    content_ar = models.TextField()
    content_en = models.TextField()

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class BlogPageSettings(models.Model):
    page_title_ar = models.CharField(max_length=300)
    page_title_en = models.CharField(max_length=300)

    last_update_title_ar = models.CharField(max_length=300)
    last_update_title_en = models.CharField(max_length=300)

    last_update_description_ar = models.TextField(blank=True)
    last_update_description_en = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Blog Page Settings"
