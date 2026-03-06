from django.db import models


class HeroSection(models.Model):
    """
    هيرو الصفحة — يدعم:
    - نص hover عربي / إنجليزي
    - عناوين وأزرار للجانب الأيسر والأيمن
    - زر / رابط مركزي مع الشعار
    - اختيار إما URL أو صفحة من الـ CMS لكل زر
    - إظهار/إخفاء الهيدر
    (الـ overlay ثابت من الـ CSS وليس من هنا)
    """
    slug = models.SlugField(unique=True)

    # Hover texts
    hover_text_ar = models.CharField(max_length=200, blank=True)
    hover_text_en = models.CharField(max_length=200, blank=True)

    # LEFT SIDE
    left_title_ar = models.CharField(max_length=200, blank=True)
    left_title_en = models.CharField(max_length=200, blank=True)

    left_button_text_ar = models.CharField(max_length=200, blank=True)
    left_button_text_en = models.CharField(max_length=200, blank=True)

    left_button_url = models.CharField(max_length=300, blank=True)
    left_button_page = models.ForeignKey(
        "Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hero_left_buttons",
    )

    # RIGHT SIDE
    right_title_ar = models.CharField(max_length=200, blank=True)
    right_title_en = models.CharField(max_length=200, blank=True)

    right_button_text_ar = models.CharField(max_length=200, blank=True)
    right_button_text_en = models.CharField(max_length=200, blank=True)

    right_button_url = models.CharField(max_length=300, blank=True)
    right_button_page = models.ForeignKey(
        "Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hero_right_buttons",
    )

    # CENTER (logo / plus)
    center_button_text_ar = models.CharField(max_length=200, blank=True)
    center_button_text_en = models.CharField(max_length=200, blank=True)

    center_button_url = models.CharField(max_length=300, blank=True)
    center_button_page = models.ForeignKey(
        "Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="hero_center_buttons",
    )

    # Control
    show_header = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.slug


class HeroMedia(models.Model):
    MEDIA_TYPES = [
        ("logo_desktop", "Logo Desktop"),
        ("logo_mobile", "Logo Mobile"),
        ("image", "Image"),
        ("video", "Video"),
    ]

    hero = models.ForeignKey(
        HeroSection, related_name="media", on_delete=models.CASCADE
    )
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    file = models.FileField(upload_to="hero/media/")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.hero.slug} – {self.media_type}"


# ================== Footer ==================

class FooterColumn(models.Model):
    key = models.CharField(max_length=50, unique=True)

    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title_ar



class Page(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("coming_soon", "Coming Soon"),
    ]

    slug = models.SlugField(unique=True)
    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)
    content_ar = models.TextField(blank=True)
    content_en = models.TextField(blank=True)

    page_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    is_published = models.BooleanField(default=True)
    show_in_sitemap = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug


class FooterLink(models.Model):
    MEDIA_TYPES = [
        ("link", "Link"),
        ("footer_logo", "Footer Logo"),
    ]

    column = models.ForeignKey(
        FooterColumn,
        related_name="links",
        on_delete=models.CASCADE
    )

    # ⭐ NEW: parent support (TREE)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE
    )

    label_ar = models.CharField(max_length=200)
    label_en = models.CharField(max_length=200)

    url = models.CharField(max_length=300, blank=True)
    page = models.ForeignKey(Page, null=True, blank=True, on_delete=models.SET_NULL)

    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPES,
        default="link",
    )
    file = models.ImageField(upload_to="footer/", null=True, blank=True)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label_ar

# ================== Home Sections ==================

class HomeSection(models.Model):
    key = models.CharField(max_length=100)
    title_ar = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)

    subtitle_ar = models.CharField(max_length=255, blank=True)
    subtitle_en = models.CharField(max_length=255, blank=True)

    body_ar = models.TextField(blank=True)
    body_en = models.TextField(blank=True)

    image = models.ImageField(upload_to="cms/sections/", blank=True, null=True)

    button_text_ar = models.CharField(max_length=100, blank=True)
    button_text_en = models.CharField(max_length=100, blank=True)
    button_link = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class HeaderLink(models.Model):
    LINK_TYPES = [
        ("link", "Link"),
        ("logo", "Logo"),
    ]

    type = models.CharField(
        max_length=10,
        choices=LINK_TYPES,
        default="link"
    )

    label_ar = models.CharField(max_length=200, blank=True)
    label_en = models.CharField(max_length=200, blank=True)

    url = models.CharField(max_length=300, blank=True, null=True)
    page = models.ForeignKey(Page, null=True, blank=True, on_delete=models.SET_NULL)

    logo = models.ImageField(
        upload_to="header/",
        null=True,
        blank=True
    )

    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

# ================== FAQ ==================

class FAQItem(models.Model):
    question_ar = models.CharField(max_length=255)
    question_en = models.CharField(max_length=255)

    answer_ar = models.TextField()
    answer_en = models.TextField()

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question_ar





    # ================== Contact Page ==================

class ContactCard(models.Model):
    CARD_TYPES = [
        ("info", "Info"),
        ("button", "Button"),
        ("form", "Form"),
        ("faq", "FAQ Preview"),
    ]

    type = models.CharField(max_length=20, choices=CARD_TYPES)

    title_ar = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    description2_ar = models.TextField(blank=True)
    description2_en = models.TextField(blank=True)

    button_label_ar = models.CharField(max_length=100, blank=True)
    button_label_en = models.CharField(max_length=100, blank=True)
    url = models.CharField(max_length=300, blank=True)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.type} — {self.title_ar}"





class ContactFAQPreview(models.Model):
    faq = models.ForeignKey(FAQItem, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)



class ContactPageSettings(models.Model):
    title_ar = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Contact Page Settings"


class PageContent(models.Model):
    slug = models.SlugField(unique=True)

    title_ar = models.CharField(max_length=255, blank=True)
    title_en = models.CharField(max_length=255, blank=True)

    content_ar = models.TextField(blank=True)
    content_en = models.TextField(blank=True)

    extra_json = models.JSONField(default=dict, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug
