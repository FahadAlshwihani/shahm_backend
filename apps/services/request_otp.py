from django.contrib.auth.hashers import (
    make_password,
    check_password,
)
import secrets
from django.db import models
from django.utils import timezone
from datetime import timedelta

class ServiceRequestOTP(models.Model):

    link = models.ForeignKey(
        "services.ServiceRequestAccessLink",
        related_name="otps",
        on_delete=models.CASCADE,
    )

    email = models.EmailField()

    code = models.CharField(
        max_length=255,
    )

    attempts = models.PositiveIntegerField(
        default=0,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def set_code(self, raw_code):
        self.code = make_password(raw_code)

    def verify_code(self, raw_code):
        return check_password(raw_code, self.code)

    @classmethod
    def generate_code(cls):
        return str(
            secrets.randbelow(900000) + 100000
        )

    @classmethod
    def expiry(cls):
        return timezone.now() + timedelta(minutes=10)