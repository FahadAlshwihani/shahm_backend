from django.db import models

class LegalPage(models.Model):
    """
    الصفحات القانونية الأساسية، قابلة للزيادة من الداش بورد.
    مثال:
    - terms-and-conditions
    - privacy-policy
    - cookies-policy
    - confidentiality-policy
    - disclaimer
    """

    slug = models.SlugField(unique=True)  # رابط الصفحة
    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)

    content_ar = models.TextField()
    content_en = models.TextField()

    is_published = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=True)  # تظهر بالفوتر أو لا

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Legal Page"
        verbose_name_plural = "Legal Pages"
        ordering = ["slug"]

    def __str__(self):
        return self.slug
