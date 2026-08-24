import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone


class ServiceRequestAccessLink(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_REVOKED = "revoked"
    STATUS_EXPIRED = "expired"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_REVOKED, "Revoked"),
        (STATUS_EXPIRED, "Expired"),
    ]

    request = models.ForeignKey(
        "services.ServiceAdvisoryRequest",
        related_name="access_links",
        on_delete=models.CASCADE,
    )

    form = models.ForeignKey(
        "form_builder.FormTemplate",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    submission = models.ForeignKey(
        "form_builder.FormSubmission",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="access_links",
    )

    snapshot_data = models.JSONField(
        default=dict,
        blank=True,
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_accessed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    edit_count = models.PositiveIntegerField(
        default=0,
    )

    max_edits = models.PositiveIntegerField(
        default=3,
    )

    editable_fields = models.JSONField(
        default=list,
        blank=True,
    )

    public_key = models.CharField(
        max_length=128,
        unique=True,
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):

        if not self.public_key:
            self.public_key = secrets.token_urlsafe(48)

        super().save(*args, **kwargs)

    @property
    def is_valid(self):

        if self.status != self.STATUS_ACTIVE:
            return False

        if self.expires_at and timezone.now() > self.expires_at:
            return False

        return True

class ServiceRequestAccessActivity(models.Model):

    ACTION_OTP_SENT = "otp_sent"
    ACTION_OTP_VERIFIED = "otp_verified"
    ACTION_OTP_FAILED = "otp_failed"
    ACTION_SNAPSHOT_VIEWED = "snapshot_viewed"
    ACTION_SUBMISSION_UPDATED = "submission_updated"
    ACTION_ACCESS_REVOKED = "access_revoked"

    ACTION_CHOICES = [
        (ACTION_OTP_SENT, "OTP Sent"),
        (ACTION_OTP_VERIFIED, "OTP Verified"),
        (ACTION_OTP_FAILED, "OTP Failed"),
        (ACTION_SNAPSHOT_VIEWED, "Snapshot Viewed"),
        (ACTION_SUBMISSION_UPDATED, "Submission Updated"),
        (ACTION_ACCESS_REVOKED, "Access Revoked"),
    ]

    link = models.ForeignKey(
        ServiceRequestAccessLink,
        on_delete=models.CASCADE,
        related_name="activities",
        null=True,
        blank=True,
    )
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.link_id} - "
            f"{self.action}"
        )

class ServiceRequestAccessSession(models.Model):
    link = models.ForeignKey(
        "services.ServiceRequestAccessLink",
        related_name="sessions",
        on_delete=models.CASCADE,
    )

    otp = models.ForeignKey(
        "services.ServiceRequestOTP",
        related_name="sessions",
        on_delete=models.CASCADE,
    )

    token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def generate_token(cls):
        return secrets.token_urlsafe(48)

    @property
    def is_valid(self):
        return timezone.now() < self.expires_at
