from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from services.request_access import (
    ServiceRequestAccessSession,
)
from .access_session import (
    AccessSessionService,
)


def validate_access_session(
        public_key,
        token,
):
    if not token:
        raise PermissionDenied(
            "Access token required."
        )

    session = (
        ServiceRequestAccessSession.objects
        .select_related("link")
        .filter(
            token=token,
            link__public_key=public_key,
        )
        .first()
    )

    if not session:
        raise PermissionDenied(
            "Invalid access token."
        )

    if not session.is_valid:
        raise PermissionDenied(
            "Access token expired."
        )

    if not session.otp:
        raise PermissionDenied(
            "OTP verification required."
        )

    validate_verified_otp(
        session.otp
    )

    return session


def validate_access_link(link):
    if link.status != link.STATUS_ACTIVE:
        raise PermissionDenied(
            "Access link is not active."
        )

    if link.expires_at and timezone.now() > link.expires_at:
        raise PermissionDenied(
            "Access link expired."
        )

    if link.edit_count >= link.max_edits:
        raise PermissionDenied(
            "Maximum edits exceeded."
        )


def validate_verified_otp(otp):
    if otp.is_verified is False:
        raise PermissionDenied(
            "OTP not verified."
        )

    if timezone.now() > otp.expires_at:
        raise PermissionDenied(
            "OTP expired."
        )
