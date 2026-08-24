from datetime import datetime
from pathlib import Path
import mimetypes
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db import IntegrityError
from django.utils import timezone

from apps.services.models import (
    AppointmentBooking,
    AppointmentSlot,
    Service,
    ServiceAdvisoryRequest,
    ServiceAdvisoryRequestItem,
    CareerApplication,
    CareerJob,
    AppointmentBookingFile,
    ServiceAdvisoryRequestFile,
)
from apps.services.utils.references import (
    generate_reference,
)

ALLOWED_DOCUMENT_MIMES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}

ALLOWED_CV_MIMES = {
    "application/pdf",
}

ALLOWED_DOCUMENT_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
}

ALLOWED_CV_EXTENSIONS = {
    ".pdf",
}

MAX_ATTACHMENT_SIZE = 5 * 1024 * 1024
MAX_VOICE_SIZE = 10 * 1024 * 1024

ALLOWED_VOICE_MIMES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
}

ALLOWED_VOICE_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".webm",
    ".ogg",
    ".m4a",
}


def get_field_value(
        form,
        cleaned_data,
        system_key,
        default=None,
        multiple=False,
):
    fields = (
        form.sections
        .filter(
            is_active=True,
            fields__system_key=system_key,
            fields__is_active=True,
        )
        .values_list(
            "fields__key",
            flat=True,
        )
    )

    field_keys = list(fields)

    if not field_keys:
        return [] if multiple else default

    values = []

    for key in field_keys:
        value = cleaned_data.get(key)

        if value in [None, "", [], {}]:
            continue

        values.append(value)

    if multiple:
        return values

    return values[-1] if values else default


def get_uploaded_files(
        form,
        files,
        system_key,
):
    field_keys = (
        form.sections
        .filter(
            is_active=True,
            fields__system_key=system_key,
            fields__is_active=True,
        )
        .values_list(
            "fields__key",
            flat=True,
        )
    )

    uploaded = []

    for key in field_keys:
        for item in files.getlist(key):
            item.field_name = key
            uploaded.append(item)

    return uploaded


def validate_uploaded_file(
        file,
        *,
        field_name,
        allowed_mimes,
        allowed_extensions,
        max_size,
        required=False,
):
    if not file:
        if required:
            raise ValidationError(f"{field_name} is required")
        return None

    extension = Path(file.name).suffix.lower()

    content_type, _ = mimetypes.guess_type(
        file.name
    )

    if not content_type:
        raise ValidationError(
            f"{field_name} file type could not be detected"
        )

    if extension not in allowed_extensions:
        raise ValidationError(
            f"{field_name} file extension is not allowed"
        )

    if content_type not in allowed_mimes:
        raise ValidationError(
            f"{field_name} file type is not allowed"
        )

    if file.size > max_size:
        raise ValidationError(
            f"{field_name} file size is too large"
        )

    return file


class BaseFormAction:
    def run(
            self,
            form,
            submission,
            cleaned_data,
            files,
    ):
        raise NotImplementedError


class AppointmentFormAction(BaseFormAction):
    @transaction.atomic
    def run(
            self,
            form,
            submission,
            cleaned_data,
            files,
    ):
        slot_id = get_field_value(
            form=form,
            cleaned_data=cleaned_data,
            system_key="slot_id",
        )

        if not slot_id:
            raise ValidationError("Slot is required")

        try:
            slot_id = int(slot_id)
        except (TypeError, ValueError):
            raise ValidationError("Invalid slot")

        slot = (
            AppointmentSlot.objects
            .select_for_update()
            .filter(
                id=slot_id,
                is_available=True,
                date__gte=timezone.localdate(),
            )
            .first()
        )

        if not slot:
            raise ValidationError("Slot not available")

        slot_datetime = timezone.make_aware(
            datetime.combine(
                slot.date,
                slot.start_time,
            ),
            timezone.get_current_timezone(),
        )

        if slot_datetime <= timezone.localtime():
            raise ValidationError(
                "This slot has already passed"
            )

        try:
            booking = AppointmentBooking.objects.create(
                slot=slot,
                form_submission=submission,
                reference=generate_reference("booking"),
                status="pending",
                slot_date_snapshot=slot.date,
                slot_start_snapshot=slot.start_time,
                slot_end_snapshot=slot.end_time,
                slot_shift_snapshot=slot.shift,
                slot_label_snapshot=(
                    f"{slot.date} | "
                    f"{slot.start_time.strftime('%I:%M %p')} - "
                    f"{slot.end_time.strftime('%I:%M %p')}"
                ),
            )

        except IntegrityError:
            raise ValidationError(
                "Slot already booked"
            )

        # =====================================
        # LOCK SLOT
        # =====================================

        slot.is_available = False
        slot.save(update_fields=["is_available"])

        # =====================================
        # FILES
        # =====================================

        attachments = [
            validate_uploaded_file(
                file,
                field_name="attachment",
                allowed_mimes=ALLOWED_DOCUMENT_MIMES,
                allowed_extensions=ALLOWED_DOCUMENT_EXTENSIONS,
                max_size=MAX_ATTACHMENT_SIZE,
                required=False,
            )
            for file in get_uploaded_files(
                form,
                files,
                "attachment",
            )
        ]

        voice_notes = [
            validate_uploaded_file(
                file,
                field_name="voice_note",
                allowed_mimes=ALLOWED_VOICE_MIMES,
                allowed_extensions=ALLOWED_VOICE_EXTENSIONS,
                max_size=MAX_VOICE_SIZE,
                required=False,
            )
            for file in get_uploaded_files(
                form,
                files,
                "voice_note",
            )
        ]

        booking_files = []

        booking_files.extend([
            AppointmentBookingFile(
                booking=booking,
                file=file,
                file_type="attachment",
                original_field_key="attachment",
            )
            for file in attachments
        ])

        booking_files.extend([
            AppointmentBookingFile(
                booking=booking,
                file=file,
                file_type="voice_note",
                original_field_key="voice_note",
            )
            for file in voice_notes
        ])

        if booking_files:
            for item in booking_files:
                item.save()

        return {
            "type": "appointment_booking",
            "booking_id": booking.id,
            "reference": booking.reference,
        }


class ServiceRequestFormAction(BaseFormAction):
    @transaction.atomic
    def run(
            self,
            form,
            submission,
            cleaned_data,
            files,
    ):
        service_ids = get_field_value(
            form=form,
            cleaned_data=cleaned_data,
            system_key="service_ids",
            multiple=True,
        )

        flattened = []

        for item in service_ids:

            # grouped structure
            if isinstance(item, dict):
                flattened.extend(
                    item.get("services", [])
                )
                continue

            # nested grouped list
            if isinstance(item, list):

                for group in item:

                    if isinstance(group, dict):
                        flattened.extend(
                            group.get("services", [])
                        )

                    else:
                        flattened.append(group)

                continue

            # fallback
            flattened.append(item)

        service_ids = flattened

        try:
            service_ids = [
                int(item)
                for item in service_ids
            ]
        except (TypeError, ValueError):
            raise ValidationError("Invalid services selected")

        if not service_ids:
            raise ValidationError("At least one service is required")

        services = Service.objects.filter(
            id__in=service_ids,
            is_active=True,
        )

        if services.count() != len(set(service_ids)):
            raise ValidationError("Invalid services selected")

        attachments = [
            validate_uploaded_file(
                file,
                field_name="attachment",
                allowed_mimes=ALLOWED_DOCUMENT_MIMES,
                allowed_extensions=ALLOWED_DOCUMENT_EXTENSIONS,
                max_size=MAX_ATTACHMENT_SIZE,
                required=False,
            )
            for file in get_uploaded_files(
                form,
                files,
                "attachment",
            )
        ]

        voice_notes = [
            validate_uploaded_file(
                file,
                field_name="voice_note",
                allowed_mimes=ALLOWED_VOICE_MIMES,
                allowed_extensions=ALLOWED_VOICE_EXTENSIONS,
                max_size=MAX_VOICE_SIZE,
                required=False,
            )
            for file in get_uploaded_files(
                form,
                files,
                "voice_note",
            )
        ]

        voice_note = (
            voice_notes[-1]
            if voice_notes
            else None
        )

        settings = form.integration_settings or {}

        title = cleaned_data.get(
            settings.get("title_field", "title"),
            "",
        )

        first_name = cleaned_data.get(
            settings.get(
                "first_name_field",
                "first_name",
            ),
            "",
        )

        last_name = cleaned_data.get(
            settings.get(
                "last_name_field",
                "last_name",
            ),
            "",
        )

        email = ""

        if form.email_field_key:
            email = cleaned_data.get(form.email_field_key, "")

        if not email:
            email = get_field_value(
                form=form,
                cleaned_data=cleaned_data,
                system_key="email",
                default="",
            )

        if not email:
            email = cleaned_data.get(
                settings.get("email_field", "email"),
                "",
            )

        if not email:
            raise ValidationError(
                "Email field is required for service request OTP."
            )

        phone = get_field_value(
            form=form,
            cleaned_data=cleaned_data,
            system_key="phone",
            default="",
        ) or cleaned_data.get(
            settings.get("phone_field", "phone"),
            "",
        )

        if isinstance(phone, dict):
            phone = (
                f"{phone.get('country_code', '')}"
                f"{phone.get('number', '')}"
            )

        phone = str(phone).strip()

        message = cleaned_data.get(
            settings.get(
                "message_field",
                "message",
            ),
            "",
        )

        request_obj = (
            ServiceAdvisoryRequest.objects.create(
                title=title,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                message=message,
                reference=generate_reference(
                    "service"
                ),
                form_submission=submission,
            )
        )

        ServiceAdvisoryRequestItem.objects.bulk_create([
            ServiceAdvisoryRequestItem(
                request=request_obj,
                service=service,
            )
            for service in services
        ])

        service_files = []

        service_files.extend([
            ServiceAdvisoryRequestFile(
                request=request_obj,
                file=file,
                file_type="attachment",
                original_field_key="attachment",
            )
            for file in attachments
        ])

        service_files.extend([
            ServiceAdvisoryRequestFile(
                request=request_obj,
                file=file,
                file_type="voice_note",
                original_field_key="voice_note",
            )
            for file in voice_notes
        ])

        if service_files:
            for file_obj in service_files:
                file_obj.save()

        return {
            "type": "service_request",
            "request_id": request_obj.id,
            "reference": request_obj.reference,
        }


class CareerApplicationFormAction(BaseFormAction):
    @transaction.atomic
    def run(
            self,
            form,
            submission,
            cleaned_data,
            files,
    ):
        job_id = get_field_value(
            form=form,
            cleaned_data=cleaned_data,
            system_key="job_id",
            default=None,
        )

        job = None

        if job_id:
            try:
                job_id = int(job_id)
            except (TypeError, ValueError):
                raise ValidationError("Selected job is invalid")

            job = CareerJob.objects.filter(
                id=job_id,
                is_active=True,
            ).first()

            if not job:
                raise ValidationError("Selected job is invalid")

        application = CareerApplication.objects.create(
            job=job,
            reference=generate_reference("career"),
            form_submission=submission,
        )

        return {
            "type": "career_application",
            "application_id": application.id,
            "reference": application.reference,
        }

FORM_ACTIONS = {
    "appointments": AppointmentFormAction(),
    "services": ServiceRequestFormAction(),
    "careers": CareerApplicationFormAction(),
}
