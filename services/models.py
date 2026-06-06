from django.db import models
from django.core.exceptions import ValidationError
from cms.models import FAQItem
from django.db import transaction
from django.utils.text import slugify
from .validators import validate_file


class ServicePageCMS(models.Model):
    hero_logo = models.ImageField(
        upload_to="services/page/logo/",
        null=True,
        blank=True,
    )

    HERO_MEDIA_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
    ]

    hero_media_type = models.CharField(
        max_length=20,
        choices=HERO_MEDIA_TYPES,
        default="image",
    )

    hero_image = models.ImageField(
        upload_to="services/page/hero/",
        null=True,
        blank=True,
    )

    hero_video = models.FileField(
        upload_to="services/page/video/",
        null=True,
        blank=True,
    )

    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    search_placeholder_ar = models.CharField(
        max_length=255,
        blank=True,
    )

    search_placeholder_en = models.CharField(
        max_length=255,
        blank=True,
    )

    # =====================================================
    # SUBMIT REQUEST BUTTON
    # =====================================================

    ACTION_TYPES = [
        ("none", "None"),
        ("url", "URL"),
        ("form_modal", "Form Modal"),
    ]

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
        related_name="services_page_buttons",
    )

    is_active = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):

        if (
                self.primary_action_type == "url"
                and not self.primary_url
        ):
            raise ValidationError(
                "primary_url required"
            )

        if (
                self.primary_action_type == "form_modal"
                and not self.primary_form
        ):
            raise ValidationError(
                "primary_form required"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return "Services Page CMS"


class PracticeArea(models.Model):
    title_ar = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    title_en = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    slug = models.SlugField(
        unique=True,
        db_index=True,
        null=True,
        blank=True,
    )

    icon = models.ImageField(
        upload_to="services/practice/icons/",
        null=True,
        blank=True,
    )


class MainService(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        null=True,
        blank=True,
    )

    title_ar = models.CharField(max_length=255)

    title_en = models.CharField(max_length=255)

    icon = models.ImageField(
        upload_to="services/main/icons/",
        null=True,
        blank=True,
    )

    slug = models.SlugField(
        unique=True,
        db_index=True,
        null=True,
        blank=True,
    )

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )

    practice_area = models.ForeignKey(
        PracticeArea,
        related_name="main_services",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title_en or self.title_ar


class Service(models.Model):
    main_service = models.ForeignKey(
        MainService,
        related_name="services",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    title_ar = models.CharField(max_length=255)

    title_en = models.CharField(max_length=255)

    slug = models.SlugField(
        unique=True,
        db_index=True,
        null=True,
        blank=True,
    )

    serial_number = models.CharField(
        max_length=50,
        db_index=True,
        blank=True,
        null=True,
    )

    short_description_ar = models.TextField(blank=True)

    short_description_en = models.TextField(blank=True)

    is_featured = models.BooleanField(default=False)

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title_en or self.title_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title_en or self.title_ar)

            slug = base_slug
            counter = 1

            while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        with transaction.atomic():

            creating = self.pk is None

            super().save(*args, **kwargs)

            if creating and not self.serial_number:
                count = (
                            Service.objects
                            .select_for_update()
                            .filter(main_service=self.main_service)
                            .exclude(pk=self.pk)
                            .count()
                        ) + 1

                self.serial_number = (
                    f"{self.main_service.code}-{count:03d}"
                )

                super().save(update_fields=["serial_number"])


class ServiceAdvisoryPage(models.Model):
    title_top_ar = models.CharField(max_length=255, blank=True)
    title_top_en = models.CharField(max_length=255, blank=True)

    description_top_ar = models.TextField(blank=True)
    description_top_en = models.TextField(blank=True)

    title_bottom_ar = models.CharField(max_length=255, blank=True)
    title_bottom_en = models.CharField(max_length=255, blank=True)

    description_bottom_ar = models.TextField(blank=True)
    description_bottom_en = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Service Advisory Page CMS"


class ServiceAdvisoryRequest(models.Model):
    title = models.CharField(max_length=50)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    reference = models.CharField(max_length=50, blank=True, null=True)

    form_submission = models.OneToOneField(
        "form_builder.FormSubmission",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="service_request",
    )

    email = models.EmailField()
    phone = models.CharField(max_length=30)

    message = models.TextField()


    STATUS_NEW = "new"
    STATUS_REVIEWING = "reviewing"
    STATUS_AWAITING_CLIENT = "awaiting_client"
    STATUS_CLIENT_UPDATED = "client_updated"
    STATUS_CONTRACTING = "contracting"
    STATUS_CLOSED = "closed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_REVIEWING, "Reviewing"),
        (STATUS_AWAITING_CLIENT, "Awaiting Client"),
        (STATUS_CLIENT_UPDATED, "Client Updated"),
        (STATUS_CONTRACTING, "Contracting"),
        (STATUS_CLOSED, "Closed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        db_index=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ServiceAdvisoryRequestFile(models.Model):
    FILE_TYPES = [
        ("attachment", "Attachment"),
        ("voice_note", "Voice Note"),
    ]

    request = models.ForeignKey(
        ServiceAdvisoryRequest,
        related_name="files",
        on_delete=models.CASCADE,
    )

    file = models.FileField(
        upload_to="service_advisory/files/",
        validators=[validate_file],
    )

    file_type = models.CharField(
        max_length=30,
        choices=FILE_TYPES,
    )

    original_field_key = models.CharField(
        max_length=150,
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return (
            f"{self.request_id} - "
            f"{self.file_type}"
        )


class ServiceAdvisoryRequestItem(models.Model):
    request = models.ForeignKey(
        ServiceAdvisoryRequest,
        related_name="items",
        on_delete=models.CASCADE
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.request.id} - {self.service.title_en}"


class ServiceSection(models.Model):
    service = models.ForeignKey(
        Service,
        related_name="sections",
        on_delete=models.CASCADE,
    )

    title_ar = models.CharField(max_length=255)

    title_en = models.CharField(max_length=255)

    subtitle_ar = models.CharField(
        max_length=255,
        blank=True,
    )

    subtitle_en = models.CharField(
        max_length=255,
        blank=True,
    )

    content_ar = models.TextField(blank=True)

    content_en = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return (
            f"{self.service.title_en} - {self.title_en}"
        )


class AppointmentSettings(models.Model):
    default_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    price_online = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    slot_duration = models.PositiveIntegerField(
        help_text="بالدقائق",
        default=30
    )
    is_active = models.BooleanField(default=True)


class AppointmentSlot(models.Model):
    SHIFT_TYPES = [
        ("morning", "Morning"),
        ("evening", "Evening"),
    ]

    date = models.DateField(db_index=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    shift = models.CharField(max_length=10, choices=SHIFT_TYPES)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ("date", "start_time")

    def __str__(self):
        return f"{self.date} {self.start_time} - {self.end_time} ({self.shift})"


class AppointmentBooking(models.Model):
    slot = models.ForeignKey(
        AppointmentSlot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    slot_date_snapshot = models.DateField(
        null=True,
        blank=True,
        db_index=True,
    )

    slot_start_snapshot = models.TimeField(
        null=True,
        blank=True,
    )

    slot_end_snapshot = models.TimeField(
        null=True,
        blank=True,
    )

    slot_shift_snapshot = models.CharField(
        max_length=10,
        blank=True,
    )

    slot_label_snapshot = models.CharField(
        max_length=255,
        blank=True,
    )

    reference = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    form_submission = models.OneToOneField(
        "form_builder.FormSubmission",
        related_name="appointment_booking",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["slot"],
                name="unique_slot_booking"
            )
        ]

class AppointmentBookingFile(models.Model):
    FILE_TYPES = [
        ("attachment", "Attachment"),
        ("voice_note", "Voice Note"),
    ]

    booking = models.ForeignKey(
        AppointmentBooking,
        related_name="files",
        on_delete=models.CASCADE,
    )

    file = models.FileField(
        upload_to="appointments/files/all/",
        validators=[validate_file],
    )

    file_type = models.CharField(
        max_length=30,
        choices=FILE_TYPES,
    )

    original_field_key = models.CharField(
        max_length=150,
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return (
            f"{self.booking_id} - "
            f"{self.file_type}"
        )


class AppointmentPage(models.Model):
    title_ar = models.CharField(max_length=255, blank=True)
    title_en = models.CharField(max_length=255, blank=True)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    footer_ar = models.TextField(blank=True)
    footer_en = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Appointment Booking Page CMS"


class ReferenceSetting(models.Model):
    type = models.CharField(max_length=50, unique=True)
    prefix = models.CharField(max_length=10, default="REF")
    current_number = models.PositiveIntegerField(default=1)


# =========================================================
# ================== CAREERS SYSTEM =======================
# =========================================================

class CareerJob(models.Model):
    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    location = models.CharField(max_length=255, blank=True)
    job_type = models.CharField(
        max_length=50,
        default="full_time"
    )

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title_ar


class CareerApplication(models.Model):
    job = models.ForeignKey(
        CareerJob,
        related_name="applications",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    reference = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(max_length=50, default="new")

    form_submission = models.OneToOneField(
        "form_builder.FormSubmission",
        related_name="career_application",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference or f"Career Application {self.pk}"


from .request_access import ServiceRequestAccessLink
from .request_otp import ServiceRequestOTP
