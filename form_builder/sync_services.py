from django.db import transaction
from services.models import (
    ServiceAdvisoryRequest,
    ServiceAdvisoryRequestItem,
    ServiceAdvisoryRequestFile,
    Service,
    AppointmentBooking,
    AppointmentBookingFile,
    AppointmentSlot,
    CareerApplication,
    CareerJob,
)


# =========================================================
# HELPERS
# =========================================================

def _ensure_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


def _latest(value, default=None):
    values = _ensure_list(value)

    if not values:
        return default

    return values[-1]


# =========================================================
# BUILD VALUES MAP
# =========================================================

def _build_values_map(submission):

    values = {}

    for value in (
        submission.values
        .select_related("field")
    ):

        field = value.field

        field_key = field.key

        # =====================================
        # VALUE
        # =====================================

        if value.value_file:
            final_value = value.value_file

        elif value.value_json is not None:
            final_value = value.value_json

        else:
            final_value = value.value_text

        # =====================================
        # MULTI SUPPORT
        # =====================================

        if field_key in values:

            existing = values[field_key]

            if isinstance(existing, list):
                existing.append(final_value)

            else:
                values[field_key] = [
                    existing,
                    final_value,
                ]

        else:
            values[field_key] = final_value

    return values


# =========================================================
# NORMALIZERS
# =========================================================

def _normalize_phone(value):

    value = _latest(value, value)

    if isinstance(value, dict):
        return (
            f'{value.get("country_code", "")}'
            f'{value.get("number", "")}'
        ).strip()

    if value:
        return str(value).strip()

    return None


def _to_int(value):

    try:

        value = _latest(value, value)

        if value in [None, ""]:
            return None

        return int(value)

    except (TypeError, ValueError):
        return None


def _to_int_list(value):

    if not value:
        return []

    values = _ensure_list(value)

    result = []

    for item in values:

        if isinstance(item, list):

            for nested_item in item:

                parsed = _to_int(nested_item)

                if parsed:
                    result.append(parsed)

        else:

            parsed = _to_int(item)

            if parsed:
                result.append(parsed)

    return list(dict.fromkeys(result))


# =========================================================
# FILE HELPERS
# =========================================================

def _create_service_request_files(
    request_obj,
    values,
):

    file_mappings = {
        "attachment": "attachment",
        "voice_note": "voice_note",
    }

    created_files = []

    for key, file_type in file_mappings.items():

        files = _ensure_list(
            values.get(key)
        )

        for uploaded_file in files:

            if not uploaded_file:
                continue

            created_files.append(
                ServiceAdvisoryRequestFile(
                    request=request_obj,
                    file=uploaded_file,
                    file_type=file_type,
                    original_field_key=key,
                )
            )

    if created_files:

        ServiceAdvisoryRequestFile.objects.bulk_create(
            created_files
        )


def _create_appointment_files(
    booking,
    values,
):

    file_mappings = {
        "attachment": "attachment",
        "voice_note": "voice_note",
    }

    created_files = []

    for key, file_type in file_mappings.items():

        files = _ensure_list(
            values.get(key)
        )

        for uploaded_file in files:

            if not uploaded_file:
                continue

            created_files.append(
                AppointmentBookingFile(
                    booking=booking,
                    file=uploaded_file,
                    file_type=file_type,
                    original_field_key=key,
                )
            )

    if created_files:

        AppointmentBookingFile.objects.bulk_create(
            created_files
        )


# =========================================================
# SERVICE REQUEST
# =========================================================

def _sync_service_request(
    request_obj,
    values,
):

    request_obj.title = _latest(
        values.get("title"),
        request_obj.title,
    )

    request_obj.first_name = _latest(
        values.get("first_name"),
        request_obj.first_name,
    )

    request_obj.last_name = _latest(
        values.get("last_name"),
        request_obj.last_name,
    )

    request_obj.email = _latest(
        values.get("email"),
        request_obj.email,
    )

    phone = _normalize_phone(
        values.get("phone")
    )

    if phone:
        request_obj.phone = phone

    request_obj.message = _latest(
        values.get("message"),
        request_obj.message,
    )

    request_obj.status = (
        ServiceAdvisoryRequest.STATUS_CLIENT_UPDATED
    )

    request_obj.save()

    # =====================================
    # MULTI FILES
    # =====================================

    _create_service_request_files(
        request_obj=request_obj,
        values=values,
    )

    # =====================================
    # SERVICES
    # =====================================

    service_ids = _to_int_list(
        values.get("service_ids")
    )

    if service_ids:

        services = Service.objects.filter(
            id__in=service_ids,
            is_active=True,
        )

        ServiceAdvisoryRequestItem.objects.filter(
            request=request_obj,
        ).delete()

        ServiceAdvisoryRequestItem.objects.bulk_create([
            ServiceAdvisoryRequestItem(
                request=request_obj,
                service=service,
            )
            for service in services
        ])


# =========================================================
# APPOINTMENT
# =========================================================
def _sync_appointment_booking(
    booking,
    values,
):
    slot_id = _to_int(
        values.get("slot_id")
    )

    if slot_id and not booking.slot_id:
        with transaction.atomic():
            slot = (
                AppointmentSlot.objects
                .select_for_update()
                .filter(
                    id=slot_id,
                    is_available=True,
                )
                .first()
            )

            if not slot:
                raise ValueError(
                    "Selected slot is no longer available"
                )

            slot.is_available = False
            slot.save(
                update_fields=["is_available"]
            )

            booking.slot = slot

            booking.slot_date_snapshot = slot.date
            booking.slot_start_snapshot = slot.start_time
            booking.slot_end_snapshot = slot.end_time
            booking.slot_shift_snapshot = slot.shift

            booking.slot_label_snapshot = (
                f"{slot.date} | "
                f"{slot.start_time.strftime('%I:%M %p')} - "
                f"{slot.end_time.strftime('%I:%M %p')}"
            )

    booking.save()


# =========================================================
# CAREER APPLICATION
# =========================================================
def _sync_career_application(
    application,
    values,
):
    job_id = _to_int(
        values.get("job_id")
    )

    if job_id:
        job = CareerJob.objects.filter(
            id=job_id,
            is_active=True,
        ).first()

        if job:
            application.job = job

    application.save()

# =========================================================
# MAIN ENTRY
# =========================================================

def sync_submission_related_models(submission):

    values = _build_values_map(
        submission
    )

    if hasattr(submission, "service_request"):

        _sync_service_request(
            submission.service_request,
            values,
        )

    if hasattr(submission, "appointment_booking"):

        _sync_appointment_booking(
            submission.appointment_booking,
            values,
        )

    if hasattr(submission, "career_application"):

        _sync_career_application(
            submission.career_application,
            values,
        )