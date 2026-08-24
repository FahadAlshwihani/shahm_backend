from django.db import models
from django.utils.text import slugify


class LegalPage(models.Model):
    slug = models.SlugField(unique=True)

    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)

    meta_title_ar = models.CharField(max_length=200, blank=True)
    meta_title_en = models.CharField(max_length=200, blank=True)

    meta_description_ar = models.TextField(blank=True)
    meta_description_en = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    is_published = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_en or self.title_ar) or "legal-page"

        self.slug = slugify(self.slug) or "legal-page"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_en or self.title_ar


class LegalSection(models.Model):
    page = models.ForeignKey(
        LegalPage,
        related_name="sections",
        on_delete=models.CASCADE,
        db_index=True
    )

    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)

    anchor = models.SlugField(blank=True)

    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order"]
        unique_together = ["page", "anchor"]

    def save(self, *args, **kwargs):
        if not self.anchor:
            base = slugify(self.title_en or self.title_ar) or "section"
            anchor = base
            counter = 1

            while LegalSection.objects.filter(
                    page=self.page,
                    anchor=anchor
            ).exclude(pk=self.pk).exists():
                anchor = f"{base}-{counter}"
                counter += 1

            self.anchor = anchor

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.page.slug} - {self.anchor}"


class LegalSubSection(models.Model):
    section = models.ForeignKey(
        LegalSection,
        related_name="subsections",
        on_delete=models.CASCADE,
        db_index=True
    )

    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)

    content_ar = models.TextField(blank=True)
    content_en = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title_en or self.title_ar
