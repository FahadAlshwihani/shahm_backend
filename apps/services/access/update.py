from django.db import (
    transaction,
)
import json
from django.core.files.uploadedfile import UploadedFile
from apps.form_builder.sync_services import (
    sync_submission_related_models,
)

from apps.form_builder.serializers import (
    PublicFormSubmitSerializer,
)
from apps.form_builder.models import (
    FormSubmissionValue,
    FormSubmissionEditLog,
)
from apps.form_builder.models import FormField

from apps.services.access.snapshot import (
    build_submission_snapshot,
)
from apps.form_builder.models import (
    FormSubmissionFile,
)


class SubmissionUpdateService:

    @classmethod
    @transaction.atomic
    def update_submission(
            cls,
            submission,
            cleaned_data,
            editable_form=None,
            link=None,
            admin_user=None,
    ):
        updated_fields = []

        is_admin_mode = admin_user is not None

        effective_form = (
                editable_form
                or getattr(link, "form", None)
                or submission.form
        )

        allowed_form_field_keys = set()

        if editable_form:
            allowed_form_field_keys = set()

            sections = (
                editable_form.sections
                .filter(is_active=True)
                .prefetch_related("fields")
            )

            for section in sections:
                for field in section.fields.filter(
                        is_active=True
                ):
                    canonical_key = field.key

                    allowed_form_field_keys.add(
                        canonical_key
                    )

        values_map = {
            value.field.key: value
            for value in (
                FormSubmissionValue.objects
                .select_related("field")
                .filter(submission=submission)
            )
        }

        serializer_helper = (
            PublicFormSubmitSerializer()
        )

        allowed_field_keys = set()

        fields_queryset = (
            FormField.objects.filter(
                section__form=effective_form,
                is_active=True,
                section__is_active=True,
            )
        )

        for field in fields_queryset:
            allowed_field_keys.add(
                field.key
            )

        for field_key, new_value in (
                cleaned_data.items()
        ):

            if field_key not in allowed_field_keys:
                continue

            value_obj = values_map.get(
                field_key
            )

            if value_obj:
                field = value_obj.field

                if not field.is_active:
                    continue

            else:
                field = (
                    FormField.objects
                    .filter(
                        section__form=effective_form,
                        is_active=True,
                        section__is_active=True,
                    )
                    .filter(
                        key=field_key
                    )
                    .select_related("section")
                    .first()
                )

                if not field:
                    continue

                value_obj = FormSubmissionValue.objects.create(
                    submission=submission,
                    field=field,
                )

            # =================================================
            # FIELD LEVEL SECURITY
            # =================================================

            if not is_admin_mode:

                # =========================================
                # FIELD NOT ALLOWED
                # =========================================

                if (
                        link
                        and link.editable_fields
                        and field.key not in link.editable_fields

                ):
                    continue

                # =========================================
                # FORM FIELD VALIDATION
                # =========================================

                canonical_key = field.key

                if (
                        editable_form
                        and canonical_key not in allowed_form_field_keys
                ):
                    continue

            # No hard block here.
            # Field access is controlled by editable_fields above.
            # Field value validation/sync must happen in sync_submission_related_models().

            # =================================================
            # FILE VALIDATION
            # =================================================

            if (
                    field.field_type == field.FIELD_FILE
                    and (
                    isinstance(
                        new_value,
                        UploadedFile,
                    )
                    or (
                            isinstance(new_value, list)
                            and any(
                        isinstance(
                            item,
                            UploadedFile,
                        )
                        for item in new_value
                    )
                    )
            )
            ):
                serializer_helper._validate_file(
                    field,
                    new_value,
                )

            old_value = (
                cls._extract_old_value(
                    value_obj
                )
            )

            is_same = False

            if (
                    field.field_type == field.FIELD_FILE
                    and isinstance(new_value, list)
            ):
                SubmissionUpdateService._replace_multiple_files(
                    value_obj,
                    new_value,
                )

                FormSubmissionEditLog.objects.create(
                    submission=submission,
                    edited_by_link=(
                        link
                        if not is_admin_mode
                        else None
                    ),
                    edited_by_admin=(
                        admin_user
                        if is_admin_mode
                        else None
                    ),
                    field_key=field_key,
                    old_value=old_value,
                    new_value=[
                        file.name
                        for file in new_value
                    ],
                )

                updated_fields.append(
                    field_key
                )

                continue

            if isinstance(new_value, UploadedFile):
                is_same = False

            elif isinstance(new_value, (dict, list)):
                is_same = (
                        json.dumps(
                            old_value,
                            sort_keys=True,
                            ensure_ascii=False,
                        )
                        ==
                        json.dumps(
                            new_value,
                            sort_keys=True,
                            ensure_ascii=False,
                        )
                )

            else:
                is_same = old_value == new_value

            if is_same:
                continue

            cls._apply_new_value(
                value_obj,
                new_value,
            )

            FormSubmissionEditLog.objects.create(
                submission=submission,
                edited_by_link=(
                    link
                    if not is_admin_mode
                    else None
                ),
                edited_by_admin=(
                    admin_user
                    if is_admin_mode
                    else None
                ),
                field_key=field_key,
                old_value=old_value,
                new_value=(
                    str(new_value)
                    if not isinstance(
                        new_value,
                        (dict, list),
                    )
                    else new_value
                ),
            )

            updated_fields.append(
                field_key
            )

        if link:
            link.snapshot_data = (
                build_submission_snapshot(
                    submission=submission,
                    editable_form=editable_form,
                )
            )

            link.edit_count += 1

            link.save(
                update_fields=[
                    "snapshot_data",
                    "edit_count",
                ]
            )

        sync_submission_related_models(
            submission
        )

        return updated_fields

    @staticmethod
    def _extract_old_value(
            value_obj
    ):
        if value_obj.value_json not in [
            None,
            {},
            [],
        ]:
            return value_obj.value_json

        if value_obj.files.exists():
            return [
                {
                    "url": item.file.url,
                    "name": item.original_name,
                }
                for item in value_obj.files.all()
                if item.file
            ]

        return value_obj.value_text

    @staticmethod
    def _apply_new_value(
            value_obj,
            new_value,
    ):

        # ============================================
        # FILE
        # ============================================
        if isinstance(
                new_value,
                UploadedFile,
        ):
            SubmissionUpdateService._replace_multiple_files(
                value_obj,
                [new_value],
            )
            return

        # ============================================
        # JSON
        # ============================================
        if isinstance(
                new_value,
                (dict, list),
        ):
            value_obj.value_json = (
                new_value
            )
            value_obj.value_text = ""

            if value_obj.value_file:
                value_obj.value_file.delete(
                    save=False
                )

            value_obj.value_file = None

        # ============================================
        # TEXT
        # ============================================
        else:
            value_obj.value_text = str(
                new_value
            )

            value_obj.value_json = None

            if value_obj.value_file:
                value_obj.value_file.delete(
                    save=False
                )

            value_obj.value_file = None

        value_obj.save()

    @staticmethod
    def _replace_multiple_files(
            value_obj,
            uploaded_files,
    ):
        for item in value_obj.files.all():
            if item.file:
                item.file.delete(save=False)
            item.delete()

        if value_obj.value_file:
            value_obj.value_file.delete(
                save=False
            )

        value_obj.value_file = None
        value_obj.value_text = ""
        value_obj.value_json = None

        value_obj.save()

        for uploaded_file in uploaded_files:
            FormSubmissionFile.objects.create(
                submission_value=value_obj,
                file=uploaded_file,
                original_name=uploaded_file.name,
            )

    @staticmethod
    def _replace_file(
            value_obj,
            uploaded_file,
    ):
        if not isinstance(
                uploaded_file,
                UploadedFile,
        ):
            return

        # حذف الملفات القديمة
        for item in value_obj.files.all():

            if item.file:
                item.file.delete(
                    save=False
                )

            item.delete()

        value_obj.value_text = ""
        value_obj.value_json = None

        # legacy cleanup
        if value_obj.value_file:
            value_obj.value_file.delete(
                save=False
            )

            value_obj.value_file = None

        value_obj.save()

        # حفظ الملف الجديد داخل FormSubmissionFile
        FormSubmissionFile.objects.create(
            submission_value=value_obj,
            file=uploaded_file,
            original_name=uploaded_file.name,
        )
