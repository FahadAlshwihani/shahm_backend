from django.db import models
from django.conf import settings
from django.utils.html import strip_tags
import math

class Category(models.Model):
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)

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

    POST_TYPE_CHOICES = (
        ("news", "News"),
        ("article", "Article"),
    )

    post_type = models.CharField(
        max_length=20,
        choices=POST_TYPE_CHOICES,
        default="news"
    )

    title_ar = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300)

    # 🔥 أهم تعديل — slug غير إجباري
    slug = models.SlugField(unique=True, blank=True, null=True)

    # صورة الغلاف — اختيارية
    cover_image = models.ImageField(upload_to="blog/covers/", blank=True, null=True)

    # صورة داخل المقال — اختيارية (ستستخدم لاحقاً لو أردت)
    image = models.ImageField(upload_to="blog/images/", blank=True, null=True)

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="posts"
    )

    tags = models.ManyToManyField(Tag, blank=True)

    content_ar = models.TextField()
    content_en = models.TextField()

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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title_ar

    @property
    def read_time(self):
        text = strip_tags(self.content_en or self.content_ar or "")
        words = len(text.split())
        minutes = math.ceil(words / 200)  # 200 كلمة بالدقيقة
        return max(1, minutes)


class BlogClause(models.Model):
    post = models.ForeignKey(
        BlogPost,
        related_name="clauses",
        on_delete=models.CASCADE
    )

    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)

    content_ar = models.TextField(blank=True, null=True)
    content_en = models.TextField(blank=True, null=True)

    order = models.IntegerField(default=0)

    class Meta:
        ordering = ["order"]


    def __str__(self):
        return self.title_ar



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



class BlogRelatedPerson(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="related_people"
    )

    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="blog/related_people/",
        blank=True,
        null=True
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name_ar
