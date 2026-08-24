from django.db import models


class DefaultSEO(models.Model):
    """
    إعدادات SEO العامة للموقع (تُستخدم كـ fallback لجميع الصفحات)
    """

    site_title = models.CharField(max_length=200, blank=True)
    site_description = models.CharField(max_length=300, blank=True)
    keywords = models.CharField(max_length=500, blank=True)

    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.CharField(max_length=300, blank=True)
    og_image = models.ImageField(upload_to="seo/", blank=True, null=True)

    twitter_title = models.CharField(max_length=200, blank=True)
    twitter_description = models.CharField(max_length=300, blank=True)
    twitter_image = models.ImageField(upload_to="seo/twitter/", blank=True, null=True)

    canonical_base = models.CharField(max_length=300, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Default SEO Settings"

    class Meta:
        verbose_name = "Default SEO"
        verbose_name_plural = "Default SEO"

    # 👇 هذا عشان لو بالغلط تم تمرير DefaultSEO إلى PageSEOSerializer
    # ما يطيح السيرفر بسبب عدم وجود slug
    @property
    def slug(self):
        return "default-seo"


class PageSEO(models.Model):
    """
    SEO مخصص لصفحات معينة:
    - cms pages
    - services
    - legal pages
    - blog posts
    """

    slug = models.SlugField(unique=True)

    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    keywords = models.CharField(max_length=500, blank=True)

    og_title = models.CharField(max_length=200, blank=True)
    og_description = models.CharField(max_length=300, blank=True)
    og_image = models.ImageField(upload_to="seo/pages/", blank=True, null=True)

    canonical_url = models.CharField(max_length=300, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page SEO"
        verbose_name_plural = "Pages SEO"

    def __str__(self):
        return self.slug
