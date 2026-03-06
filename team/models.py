from django.db import models


# =========================================
# CATEGORIES (الفلاتر)
# =========================================

class TeamCategory(models.Model):
    name_ar = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name_ar


# =========================================
# MEMBERS
# =========================================

class TeamMember(models.Model):

    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)

    experience_ar = models.TextField(blank=True)
    experience_en = models.TextField(blank=True)

    profile_image = models.ImageField(
        upload_to="team/members/",
        blank=True,
        null=True
    )

    # المجال
    field_ar = models.CharField(max_length=150, blank=True)
    field_en = models.CharField(max_length=150, blank=True)

    # القطاع
    sector_ar = models.CharField(max_length=150, blank=True)
    sector_en = models.CharField(max_length=150, blank=True)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name_ar"]

    def __str__(self):
        return self.name_ar


# =========================================
# TEAM PAGE CMS (كل محتوى الصفحة)
# =========================================

class TeamPage(models.Model):

    # ===== Header =====
    title_ar = models.CharField(max_length=255, blank=True)
    title_en = models.CharField(max_length=255, blank=True)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    # ===== Hero Top =====
    hero_image = models.ImageField(
        upload_to="team/hero/",
        blank=True,
        null=True
    )

    hero_description_ar = models.TextField(blank=True)
    hero_description_en = models.TextField(blank=True)

    # ===== Middle Content =====
    content_ar = models.TextField(blank=True)
    content_en = models.TextField(blank=True)

    # ===== Bottom Hero =====
    bottom_image = models.ImageField(
        upload_to="team/bottom/",
        blank=True,
        null=True
    )

    # ===== CTA Buttons =====
    left_link_text_ar = models.CharField(max_length=200, blank=True)
    left_link_text_en = models.CharField(max_length=200, blank=True)
    left_link_url = models.CharField(max_length=500, blank=True)
    left_link_visible = models.BooleanField(default=True)

    right_link_text_ar = models.CharField(max_length=200, blank=True)
    right_link_text_en = models.CharField(max_length=200, blank=True)
    right_link_url = models.CharField(max_length=500, blank=True)
    right_link_visible = models.BooleanField(default=True)

    # ===== CTA Titles (Separate for each button) =====
    left_cta_title_ar = models.TextField(blank=True)
    left_cta_title_en = models.TextField(blank=True)

    right_cta_title_ar = models.TextField(blank=True)
    right_cta_title_en = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Team Page CMS"
