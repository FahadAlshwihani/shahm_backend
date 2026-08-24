from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid
import os


class FormTemplate(models.Model):
    title_ar = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255, blank=True)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    slug = models.SlugField(max_length=180, unique=True, blank=True)

    terms_text_ar = models.TextField(blank=True)
    terms_text_en = models.TextField(blank=True)

    require_terms_approval = models.BooleanField(default=False)

    submit_button_text_ar = models.CharField(max_length=100, default="إرسال")
    submit_button_text_en = models.CharField(max_length=100, default="Submit")

    email_field_key = models.CharField(
        max_length=100,
        blank=True,
    )

    allow_public_edit = models.BooleanField(
        default=False,
    )

    allow_admin_edit = models.BooleanField(
        default=True,
    )

    success_response = models.ForeignKey(
        "SuccessResponse",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="forms",
    )

    is_active = models.BooleanField(default=True)

    requires_login = models.BooleanField(default=False)
    requires_verification = models.BooleanField(
        default=False
    )

    allow_multiple_submissions = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_form_templates",
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    object_id = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    linked_object = GenericForeignKey(
        "content_type",
        "object_id",
    )

    FORM_CONTEXT_CHOICES = [
        ("generic", "Generic"),
        ("appointments", "Appointments"),
        ("services", "Services"),
        ("careers", "Careers"),
    ]

    context_type = models.CharField(
        max_length=50,
        choices=FORM_CONTEXT_CHOICES,
        default="generic",
    )

    FORM_TYPE_DYNAMIC = "dynamic"
    FORM_TYPE_INFO = "info"

    FORM_TYPE_CHOICES = [
        (FORM_TYPE_DYNAMIC, "Dynamic Form"),
        (FORM_TYPE_INFO, "Info Form"),
    ]

    form_type = models.CharField(
        max_length=20,
        choices=FORM_TYPE_CHOICES,
        default=FORM_TYPE_DYNAMIC,
        db_index=True,
    )

    integration_settings = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.title_ar or self.title_en or self.slug


class FormSection(models.Model):
    form = models.ForeignKey(
        FormTemplate,
        related_name="sections",
        on_delete=models.CASCADE,
    )

    title_ar = models.CharField(max_length=255, blank=True)
    title_en = models.CharField(max_length=255, blank=True)

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["form", "order"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.title_ar or self.title_en or f"Section {self.pk}"


class FormField(models.Model):
    FIELD_TEXT = "text"
    FIELD_TEXTAREA = "textarea"
    FIELD_EMAIL = "email"
    FIELD_PHONE = "phone"
    FIELD_NUMBER = "number"
    FIELD_DATE = "date"
    FIELD_SELECT = "select"
    FIELD_RADIO = "radio"
    FIELD_CHECKBOX = "checkbox"
    FIELD_FILE = "file"
    FIELD_HIDDEN = "hidden"

    FIELD_TYPES = [
        (FIELD_TEXT, "Text"),
        (FIELD_TEXTAREA, "Textarea"),
        (FIELD_EMAIL, "Email"),
        (FIELD_PHONE, "Phone"),
        (FIELD_NUMBER, "Number"),
        (FIELD_DATE, "Date"),
        (FIELD_SELECT, "Select"),
        (FIELD_RADIO, "Radio"),
        (FIELD_CHECKBOX, "Checkbox"),
        (FIELD_FILE, "File"),
        (FIELD_HIDDEN, "Hidden"),
    ]

    SYSTEM_FIELD_KEYS = [
        ("title", "Title"),
        ("first_name", "First Name"),
        ("last_name", "Last Name"),
        ("first_name_ar", "First Name Arabic"),
        ("last_name_ar", "Last Name Arabic"),
        ("email", "Email"),
        ("phone", "Phone"),
        ("message", "Message"),
        ("service_category_id", "Service Category ID"),
        ("service_ids", "Service IDs"),
        ("job_id", "Job ID"),
        ("slot_id", "Slot ID"),
        ("appointment_date", "Appointment Date"),
        ("appointment_period", "Appointment Period"),
        ("appointment_type", "Appointment Type"),
        ("visitors", "Visitors"),
        ("attachment", "Attachment"),
        ("voice_note", "Voice Note"),
        ("cv_file", "CV File"),
        ("cover_letter", "Cover Letter"),
        ("nationality", "Nationality"),
        ("gender", "Gender"),
        ("location", "Location"),
        ("source", "Source"),
        ("id_number", "ID Number"),
        ("certifications", "Certifications"),
        ("linkedin", "LinkedIn"),
        ("notes", "Notes"),
    ]

    SOURCE_STATIC = "static"
    SOURCE_DYNAMIC = "dynamic"

    OPTION_SOURCE_CHOICES = [
        (SOURCE_STATIC, "Static"),
        (SOURCE_DYNAMIC, "Dynamic"),
    ]

    DYNAMIC_SOURCE_CHOICES = [
        ("service_categories", "Service Categories"),
        ("services", "Services"),
        ("career_jobs", "Career Jobs"),
        ("appointment_slots", "Appointment Slots"),
        ("appointment_periods", "Appointment Periods"),
    ]

    dynamic_source = models.CharField(
        max_length=100,
        choices=DYNAMIC_SOURCE_CHOICES,
        blank=True,
    )

    option_source = models.CharField(
        max_length=20,
        choices=OPTION_SOURCE_CHOICES,
        default=SOURCE_STATIC,
    )

    WIDTH_FULL = "full"
    WIDTH_HALF = "half"
    WIDTH_THIRD = "third"

    WIDTH_CHOICES = [
        (WIDTH_FULL, "Full"),
        (WIDTH_HALF, "Half"),
        (WIDTH_THIRD, "Third"),
    ]

    section = models.ForeignKey(
        FormSection,
        related_name="fields",
        on_delete=models.CASCADE,
    )

    field_type = models.CharField(max_length=30, choices=FIELD_TYPES)
    key = models.SlugField(
        max_length=100,
        blank=True,
    )

    system_key = models.CharField(
        max_length=100,
        choices=SYSTEM_FIELD_KEYS,
        blank=True,
        db_index=True,
    )
    label_ar = models.CharField(max_length=255)
    label_en = models.CharField(max_length=255, blank=True)

    placeholder_ar = models.CharField(max_length=255, blank=True)
    placeholder_en = models.CharField(max_length=255, blank=True)

    help_text_ar = models.CharField(max_length=255, blank=True)
    help_text_en = models.CharField(max_length=255, blank=True)

    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    width = models.CharField(max_length=20, choices=WIDTH_CHOICES, default=WIDTH_FULL)

    validation_rules = models.JSONField(default=dict, blank=True)
    settings = models.JSONField(default=dict, blank=True)
    allow_public_edit = models.BooleanField(
        default=True,
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        unique_together = [
            ["section", "key"],
        ]
        indexes = [
            models.Index(fields=["section", "order"]),
            models.Index(fields=["field_type"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["option_source"]),
            models.Index(fields=["dynamic_source"]),
            models.Index(fields=["system_key"]),
            models.Index(fields=["allow_public_edit"]),
        ]

        constraints = []

    @property
    def form(self):
        return self.section.form

    def __str__(self):
        return f"{self.section_id} - {self.key}"

    def clean(self):
        if self.field_type in [self.FIELD_SELECT, self.FIELD_RADIO] and self.pk:
            if not self.options.exists():
                pass

        if self.field_type == self.FIELD_FILE:
            allowed_extensions = self.validation_rules.get("allowed_extensions", [])
            if allowed_extensions and not isinstance(allowed_extensions, list):
                raise ValidationError("allowed_extensions must be a list")

        if self.option_source == self.SOURCE_DYNAMIC:
            if self.field_type not in [
                self.FIELD_SELECT,
                self.FIELD_RADIO,
                self.FIELD_CHECKBOX,
            ]:
                raise ValidationError(
                    "Dynamic source is only allowed for select, radio, or checkbox fields."
                )

            if not self.dynamic_source:
                raise ValidationError(
                    "dynamic_source is required when option_source is dynamic."
                )

        if self.option_source == self.SOURCE_STATIC:
            self.dynamic_source = ""

        if not self.key and not self.system_key:
            raise ValidationError(
                "field key or system_key is required"
            )

        # =========================================
        # ALLOW REPEATED SYSTEM KEYS
        # =========================================
        # Some forms may require:
        # attachment
        # attachment_1
        # attachment_2
        #
        # We only require unique generated field.key
        # while allowing repeated logical system keys.

    def _generate_unique_key(self, base_key):
        """
        Generate unique key inside same section.

        Example:
            attachment
            attachment_1
            attachment_2
        """

        base_key = (
            slugify(
                base_key,
                allow_unicode=False,
            ).replace("-", "_")
        )

        if not base_key:
            base_key = "field"

        candidate = base_key
        counter = 1

        while (
                FormField.objects.filter(
                    section=self.section,
                    key=candidate,
                )
                        .exclude(pk=self.pk)
                        .exists()
        ):
            candidate = f"{base_key}_{counter}"
            counter += 1

        return candidate

    def save(self, *args, **kwargs):
        if self.pk:
            original = (
                FormField.objects
                .filter(pk=self.pk)
                .only("key")
                .first()
            )

            if original and original.key != self.key:
                if self.submission_values.exists():
                    raise ValidationError(
                        "Field key cannot be modified after submissions exist."
                    )

        if not self.key:
            source_key = (
                    self.system_key
                    or self.label_en
                    or self.label_ar
                    or "field"
            )

            self.key = self._generate_unique_key(
                source_key
            )

        self.key = (
            slugify(
                self.key,
                allow_unicode=False,
            )
            .replace("-", "_")
        )

        self.full_clean()

        super().save(*args, **kwargs)


class FormFieldOption(models.Model):
    field = models.ForeignKey(
        FormField,
        related_name="options",
        on_delete=models.CASCADE,
    )

    label_ar = models.CharField(max_length=255)
    label_en = models.CharField(max_length=255, blank=True)
    value = models.SlugField(max_length=120)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ["field", "value"]

    def __str__(self):
        return self.label_ar or self.value

    def _generate_unique_value(
            self,
            base_value,
    ):
        """
        Generate:
        select
        select_1
        select_2
        """

        base_value = (
            slugify(
                base_value,
                allow_unicode=False,
            )
            .replace("-", "_")
        )

        if not base_value:
            base_value = "option"

        candidate = base_value

        counter = 1

        while (
                FormFieldOption.objects.filter(
                    field=self.field,
                    value=candidate,
                )
                        .exclude(pk=self.pk)
                        .exists()
        ):
            candidate = (
                f"{base_value}_{counter}"
            )

            counter += 1

        return candidate

    def save(self, *args, **kwargs):

        original_value = None

        if self.pk:

            original = (
                FormFieldOption.objects
                .filter(pk=self.pk)
                .only("value")
                .first()
            )

            if original:
                original_value = original.value

        # =====================================
        # AUTO GENERATE VALUE
        # =====================================

        if not self.value:

            source = (
                    self.label_en
                    or self.label_ar
                    or "option"
            )

            generated = (
                slugify(
                    source,
                    allow_unicode=False,
                )
                .replace("-", "_")
            )

            self.value = (
                self._generate_unique_value(
                    generated
                )
            )

        else:

            normalized = (
                slugify(
                    self.value,
                    allow_unicode=False,
                )
                .replace("-", "_")
            )

            # only regenerate if changed
            if normalized != original_value:
                normalized = (
                    self._generate_unique_value(
                        normalized
                    )
                )

            self.value = normalized

        self.full_clean()

        super().save(*args, **kwargs)


class FormSubmission(models.Model):
    STATUS_NEW = "new"
    STATUS_REVIEWED = "reviewed"
    STATUS_ARCHIVED = "archived"

    STATUS_CHOICES = [
        (STATUS_NEW, "New"),
        (STATUS_REVIEWED, "Reviewed"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    form = models.ForeignKey(
        FormTemplate,
        related_name="submissions",
        on_delete=models.CASCADE,
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="form_submissions",
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    public_reference = models.CharField(
        max_length=40,
        unique=True,
        blank=True,
    )

    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    public_edit_token = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        null=True,
        db_index=True,
    )

    public_edit_expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.public_reference:
            self.public_reference = (
                f"AARC-{uuid.uuid4().hex[:10].upper()}"
            )

        if not self.public_edit_token:
            self.public_edit_token = uuid.uuid4().hex

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-submitted_at"]
        indexes = [
            models.Index(fields=["form", "status"]),
            models.Index(fields=["submitted_at"]),
        ]

    def __str__(self):
        return f"{self.form.slug} - {self.submitted_at}"


def submission_upload_path(instance, filename):
    extension = filename.split(".")[-1].lower()

    return (
        f"form-submissions/"
        f"{uuid.uuid4().hex}.{extension}"
    )


class FormSubmissionValue(models.Model):
    submission = models.ForeignKey(
        FormSubmission,
        related_name="values",
        on_delete=models.CASCADE,
    )

    field = models.ForeignKey(
        FormField,
        on_delete=models.PROTECT,
        related_name="submission_values",
    )

    value_text = models.TextField(blank=True)
    value_json = models.JSONField(null=True, blank=True)
    value_file = models.FileField(
        upload_to=submission_upload_path,
        null=True,
        blank=True,
    )

    class Meta:
        unique_together = ["submission", "field"]
        indexes = [
            models.Index(fields=["field"]),
            models.Index(fields=["submission"]),
            models.Index(fields=["submission", "field"]),
        ]

    def __str__(self):
        return f"{self.submission_id} - {self.field.key}"


class FormSubmissionFile(models.Model):
    submission_value = models.ForeignKey(
        FormSubmissionValue,
        related_name="files",
        on_delete=models.CASCADE,
    )

    file = models.FileField(
        upload_to=submission_upload_path,
    )

    original_name = models.CharField(
        max_length=255,
        blank=True,
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["id"]

    def save(self, *args, **kwargs):
        if (
                self.file
                and not self.original_name
        ):
            self.original_name = (
                os.path.basename(
                    self.file.name
                )
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.original_name or str(self.pk)


class FormSubmissionEditLog(models.Model):
    submission = models.ForeignKey(
        FormSubmission,
        related_name="edit_logs",
        on_delete=models.CASCADE,
    )

    edited_by_link = models.ForeignKey(
        "services.ServiceRequestAccessLink",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    edited_by_admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="submission_edit_logs",
    )

    field_key = models.CharField(
        max_length=100,
    )

    old_value = models.JSONField(
        null=True,
        blank=True,
    )

    new_value = models.JSONField(
        null=True,
        blank=True,
    )

    edited_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-edited_at"]


class SuccessResponse(models.Model):
    slug = models.SlugField(unique=True)

    # HEADER
    logo = models.ImageField(
        upload_to="forms/success/",
        null=True,
        blank=True,
    )

    # TITLES
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

    # BODY
    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    # REQUEST NUMBER
    show_reference_number = models.BooleanField(
        default=False
    )

    reference_prefix = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    # BUTTON
    button_label_ar = models.CharField(
        max_length=100,
        blank=True,
    )

    button_label_en = models.CharField(
        max_length=100,
        blank=True,
    )

    button_action_type = models.CharField(
        max_length=20,
        choices=[
            ("none", "None"),
            ("close", "Close"),
            ("url", "URL"),
        ],
        default="close",
    )

    button_url = models.CharField(
        max_length=500,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.slug


class InfoModal(models.Model):
    slug = models.SlugField(unique=True)

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

    description_ar = models.TextField(blank=True)
    description_en = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.slug

    def save(self, *args, **kwargs):

        if not self.slug:

            base = slugify(
                self.title_en or self.title_ar
            )

            slug = base
            counter = 1

            while InfoModal.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class InfoModalSection(models.Model):
    modal = models.ForeignKey(
        InfoModal,
        related_name="sections",
        on_delete=models.CASCADE,
    )

    title_ar = models.CharField(
        max_length=255,
        blank=True,
    )

    title_en = models.CharField(
        max_length=255,
        blank=True,
    )

    subtitle_ar = models.CharField(
        max_length=255,
        blank=True,
    )

    subtitle_en = models.CharField(
        max_length=255,
        blank=True,
    )

    body_ar = models.TextField(blank=True)
    body_en = models.TextField(blank=True)

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title_ar or self.title_en or str(self.id)
