from django.db import models
from cms.models import FAQItem


class PracticeArea(models.Model):
    """
    المجالات القانونية الأساسية:
    - القانون التجاري
    - القانون الجنائي
    - القانون العمالي
    - فض المنازعات
    - القانون الإداري
    ...الخ
    """
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)

    slug = models.SlugField(unique=True)

    icon = models.CharField(max_length=100, blank=True, null=True)
    cover_image = models.ImageField(upload_to="services/covers/", blank=True, null=True)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    show_on_home = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Practice Area"
        verbose_name_plural = "Practice Areas"

    def __str__(self):
        return self.name_ar


class Service(models.Model):
    practice_area = models.ForeignKey(
        PracticeArea,
        on_delete=models.CASCADE,
        related_name="services"
    )

    cover_image = models.ImageField(
        upload_to="services/items/",
        blank=True,
        null=True
    )

    title_ar = models.CharField(max_length=300)
    title_en = models.CharField(max_length=300)
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    slug = models.SlugField(unique=True)
    serial_number = models.CharField(max_length=50, blank=True)
    icon = models.CharField(max_length=100, blank=True)

    is_most_requested = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    faqs = models.ManyToManyField(
        FAQItem,
        blank=True,
        related_name="services"
    )

    overview_ar = models.TextField(blank=True)
    overview_en = models.TextField(blank=True)

    who_for_ar = models.TextField(blank=True)
    who_for_en = models.TextField(blank=True)

    scope_ar = models.TextField(blank=True)
    scope_en = models.TextField(blank=True)

    deliverables_ar = models.TextField(blank=True)
    deliverables_en = models.TextField(blank=True)

    how_it_works_ar = models.TextField(blank=True)
    how_it_works_en = models.TextField(blank=True)

    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

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
    title = models.CharField(max_length=50)  # اللقب
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    reference = models.CharField(max_length=50, blank=True, null=True)

    email = models.EmailField()
    phone = models.CharField(max_length=30)

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    message = models.TextField()

    attachment = models.FileField(
        upload_to="service_advisory/",
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=50,
        default="new"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"



class AppointmentSettings(models.Model):
    price = models.DecimalField(
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
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ("date", "start_time")


class AppointmentBooking(models.Model):
    slot = models.ForeignKey(AppointmentSlot, on_delete=models.PROTECT)
    reference = models.CharField(max_length=50, blank=True, null=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
        ],
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)


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

    # EN
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)

    # AR
    first_name_ar = models.CharField(max_length=120, blank=True)
    last_name_ar = models.CharField(max_length=120, blank=True)

    phone = models.CharField(max_length=30)
    email = models.EmailField()

    nationality = models.CharField(max_length=120, blank=True)
    gender = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=120, blank=True)
    source = models.CharField(max_length=120, blank=True)

    id_number = models.CharField(max_length=120, blank=True)
    certifications = models.TextField(blank=True)

    linkedin = models.CharField(max_length=300, blank=True)

    cv_file = models.FileField(upload_to="careers/cv/")
    cover_letter = models.FileField(upload_to="careers/cover/", null=True, blank=True)

    notes = models.TextField(blank=True)

    status = models.CharField(max_length=50, default="new")

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
