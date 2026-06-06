from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class HeroSection(models.Model):
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
    left_button_slug = models.CharField(
        max_length=300,
        blank=True,
        help_text="/contact"
    )
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
    right_button_slug = models.CharField(
        max_length=300,
        blank=True,
        help_text="/about"
    )
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

    def clean(self):
        # LEFT BUTTON
        left_targets = sum([
            bool(self.left_button_page),
            bool(self.left_button_url),
            bool(self.left_button_slug),
        ])

        if left_targets > 1:
            raise ValidationError(
                "Choose only one of left_button_page, left_button_url or left_button_slug"
            )

        if self.left_button_slug and not self.left_button_slug.startswith("/"):
            raise ValidationError({
                "left_button_slug": "Must start with /"
            })

        # RIGHT BUTTON
        right_targets = sum([
            bool(self.right_button_page),
            bool(self.right_button_url),
            bool(self.right_button_slug),
        ])

        if right_targets > 1:
            raise ValidationError(
                "Choose only one of right_button_page, right_button_url or right_button_slug"
            )

        if self.right_button_slug and not self.right_button_slug.startswith("/"):
            raise ValidationError({
                "right_button_slug": "Must start with /"
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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

    def clean(self):
        allowed_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".mp4",
            ".mov",
            ".webm",
        )

        if self.file:
            filename = self.file.name.lower()

            if not filename.endswith(allowed_extensions):
                raise ValidationError(
                    "unsupported media file type"
                )

            if self.file.size > 50 * 1024 * 1024:
                raise ValidationError(
                    "max file size is 50MB"
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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

    def clean(self):

        if self.page and self.url:
            raise ValidationError("choose page OR url")

        if self.page and self.url:
            raise ValidationError("choose page OR url")

        if self.media_type == "footer_logo" and not self.file:
            raise ValidationError("footer_logo requires file")

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)


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
        ("quick_access", "Quick Access"),
        ("menu_image", "Menu Image"),
    ]
    LOGO_VARIANTS = [
        ("full_ar", "Full Arabic"),
        ("scroll_ar", "Scroll Arabic"),
        ("full_en", "Full English"),
        ("scroll_en", "Scroll English"),
    ]

    type = models.CharField(
        max_length=20,
        choices=LINK_TYPES,
        default="link"
    )

    logo_variant = models.CharField(
        max_length=20,
        choices=LOGO_VARIANTS,
        blank=True
    )

    label_ar = models.CharField(max_length=200, blank=True)
    label_en = models.CharField(max_length=200, blank=True)

    description_ar = models.CharField(max_length=255, blank=True)
    description_en = models.CharField(max_length=255, blank=True)

    slug = models.CharField(
        max_length=200,
        blank=True,
        help_text="/contact"
    )

    url = models.CharField(
        max_length=300,
        blank=True,
        null=True
    )

    page = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    image = models.ImageField(
        upload_to="header/menu/",
        null=True,
        blank=True
    )

    logo = models.ImageField(
        upload_to="header/",
        null=True,
        blank=True
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def clean(self):
        selected_targets = sum([
            bool(self.page),
            bool(self.url),
            bool(self.slug),
        ])

        if selected_targets > 1:
            raise ValidationError(
                "choose only one of page, url or slug"
            )

        if self.slug and not self.slug.startswith("/"):
            raise ValidationError("slug must start with /")

        if self.type == "logo" and not self.logo_variant:
            raise ValidationError("logo must define variant")

        if self.type == "menu_image":
            if not self.page and not self.url and not self.slug:
                raise ValidationError("menu_image must have page or url or slug")

    # ================== FAQ ==================


class FAQCategory(models.Model):
    title_ar = models.CharField(max_length=200)
    title_en = models.CharField(max_length=200)

    slug = models.SlugField(unique=True, blank=True)

    icon = models.ImageField(upload_to="faq/icons/", null=True, blank=True)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def validate_icon(self):
        file = self.icon
        if file:
            if file.size > 2 * 1024 * 1024:
                raise ValidationError("Max size 2MB")

            if not file.name.lower().endswith((".png", ".jpg", ".jpeg", ".svg")):
                raise ValidationError("Invalid file type")

    def clean(self):
        self.validate_icon()

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title_en or self.title_ar)
            slug = base
            counter = 1

            while FAQCategory.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1

            self.slug = slug

        self.full_clean()  # 🔥 مهم جدًا
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_ar


class FAQItem(models.Model):
    category = models.ForeignKey(
        FAQCategory,
        related_name="faqs",
        on_delete=models.CASCADE,
        null=False,
        blank=False
    )

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
        ("default", "Default"),
        ("faq_preview", "FAQ Preview"),
    ]

    ACTION_TYPES = [
        ("none", "None"),
        ("url", "URL"),
        ("form_modal", "Form Modal"),
        ("info_modal", "Info Modal"),
        ("contact_request", "Contact Request"),
    ]

    type = models.CharField(
        max_length=20,
        choices=CARD_TYPES,
        default="default",
    )

    title_ar = models.CharField(max_length=200, blank=True)
    title_en = models.CharField(max_length=200, blank=True)

    subtitle_ar = models.CharField(max_length=255, blank=True)
    subtitle_en = models.CharField(max_length=255, blank=True)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    # =========================
    # PRIMARY BUTTON
    # =========================

    primary_button_label_ar = models.CharField(
        max_length=100,
        blank=True,
    )

    primary_button_label_en = models.CharField(
        max_length=100,
        blank=True,
    )

    primary_action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        default="none",
    )

    primary_url = models.CharField(
        max_length=500,
        blank=True,
    )

    primary_form = models.ForeignKey(
        "form_builder.FormTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contact_primary_cards",
    )

    primary_info_modal = models.ForeignKey(
        "form_builder.InfoModal",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="primary_contact_cards",
    )

    secondary_info_modal = models.ForeignKey(
        "form_builder.InfoModal",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="secondary_contact_cards",
    )

    # =========================
    # SECONDARY BUTTON
    # =========================

    secondary_button_label_ar = models.CharField(
        max_length=100,
        blank=True,
    )

    secondary_button_label_en = models.CharField(
        max_length=100,
        blank=True,
    )

    secondary_action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        default="none",
    )

    secondary_url = models.CharField(
        max_length=500,
        blank=True,
    )

    secondary_form = models.ForeignKey(
        "form_builder.FormTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contact_secondary_cards",
    )

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title_ar or self.title_en or str(self.id)

    def clean(self):
        if self.primary_action_type == "url" and not self.primary_url:
            raise ValidationError("primary_url required")

        if self.primary_action_type == "form_modal" and not self.primary_form:
            raise ValidationError("primary_form required")

        if self.primary_action_type == "info_modal" and not self.primary_info_modal:
            raise ValidationError("primary_info_modal required")

        if self.secondary_action_type == "url" and not self.secondary_url:
            raise ValidationError("secondary_url required")

        if self.secondary_action_type == "form_modal" and not self.secondary_form:
            raise ValidationError("secondary_form required")

        if self.secondary_action_type == "info_modal" and not self.secondary_info_modal:
            raise ValidationError("secondary_info_modal required")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


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


class FooterSettings(models.Model):
    logo_ar = models.ImageField(upload_to="footer/", null=True, blank=True)

    logo_en = models.ImageField(upload_to="footer/", null=True, blank=True)

    vat_logo = models.ImageField(upload_to="footer/", null=True, blank=True)

    newsletter_title_ar = models.CharField(max_length=255, blank=True)

    newsletter_title_en = models.CharField(max_length=255, blank=True)

    copyright_ar = models.CharField(max_length=255, blank=True)

    copyright_en = models.CharField(max_length=255, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Footer Settings"


class FooterCTA(models.Model):
    title_ar = models.CharField(max_length=150)

    title_en = models.CharField(max_length=150)

    description_ar = models.CharField(max_length=255, blank=True)

    description_en = models.CharField(max_length=255, blank=True)

    page = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    url = models.CharField(max_length=300, blank=True)

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title_ar


class AboutPage(models.Model):
    slug = models.SlugField(unique=True, default="about")

    logo = models.ImageField(upload_to="about/", null=True, blank=True)
    mobile_logo = models.ImageField(
        upload_to="about/",
        null=True,
        blank=True
    )
    media = models.FileField(upload_to="about/", null=True, blank=True)

    partners_subtitle_ar = models.CharField(max_length=255, blank=True)
    partners_subtitle_en = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "About Page"


class AboutStat(models.Model):
    page = models.ForeignKey(AboutPage, related_name="stats", on_delete=models.CASCADE)

    number = models.CharField(max_length=50)  # "24/7"
    label_ar = models.CharField(max_length=255)
    label_en = models.CharField(max_length=255)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]


class AboutPost(models.Model):
    page = models.ForeignKey(AboutPage, related_name="posts", on_delete=models.CASCADE)

    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)

    subtitle_ar = models.CharField(max_length=255, blank=True)
    subtitle_en = models.CharField(max_length=255, blank=True)

    body_ar = models.TextField(blank=True)
    body_en = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="about/posts/",
        null=True,
        blank=True
    )

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]


class AboutSection(models.Model):
    page = models.ForeignKey(AboutPage, related_name="sections", on_delete=models.CASCADE)

    key = models.CharField(max_length=100)  # مثلا: "mission", "vision"

    title_ar = models.CharField(max_length=255, blank=True)
    title_en = models.CharField(max_length=255, blank=True)

    subtitle_ar = models.CharField(max_length=255, blank=True)
    subtitle_en = models.CharField(max_length=255, blank=True)

    body_ar = models.TextField(blank=True)
    body_en = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class AboutIcon(models.Model):
    section = models.ForeignKey(AboutSection, related_name="icons", on_delete=models.CASCADE)

    icon = models.ImageField(upload_to="about/icons/")
    label_ar = models.CharField(max_length=255)
    label_en = models.CharField(max_length=255)

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]


class AboutPartner(models.Model):
    page = models.ForeignKey(AboutPage, related_name="partners", on_delete=models.CASCADE)

    logo = models.ImageField(upload_to="about/partners/")

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
