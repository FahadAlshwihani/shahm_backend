from django.conf import settings

from apps.form_builder.models import (
    FormSubmissionValue,
)
from apps.services.models import (
    MainService,
    Service,
)

def normalize_id(value):
    if isinstance(value, dict):
        value = value.get("id")

    if value in [None, ""]:
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def resolve_service_groups(value):
    if not isinstance(value, list):
        return value

    resolved = []

    for group in value:
        if not isinstance(group, dict):
            continue

        main_service_id = normalize_id(
            group.get("main_service")
            or group.get("main_service_id")
        )

        service_ids = [
            normalize_id(item)
            for item in group.get("services", [])
        ]

        service_ids = [
            item
            for item in service_ids
            if item not in [None, ""]
        ]

        main_service = None

        if main_service_id:
            main_service = MainService.objects.filter(
                id=main_service_id
            ).first()

        services = Service.objects.filter(
            id__in=service_ids,
            is_active=True,
        )

        resolved.append({
            "main_service_id": main_service_id,
            "main_service_title_ar": (
                main_service.title_ar
                if main_service else ""
            ),
            "main_service_title_en": (
                main_service.title_en
                if main_service else ""
            ),
            "services": [
                {
                    "id": service.id,
                    "title_ar": service.title_ar,
                    "title_en": service.title_en,
                }
                for service in services
            ],
        })

    return resolved


def build_submission_snapshot(
        submission,
        editable_form=None,
):
    snapshot = {}

    editable_keys = set()

    if editable_form:
        editable_keys = set()

        editable_fields = (
            editable_form.sections
            .filter(is_active=True)
            .values(
                "fields__key",
                "fields__system_key",
            )
        )

        for item in editable_fields:
            if item["fields__key"]:
                editable_keys.add(
                    item["fields__key"]
                )

    values = (
        FormSubmissionValue.objects
        .select_related("field")
        .prefetch_related(
            "field__options",
            "files",
        )
        .filter(submission=submission)
    )

    for value in values:
        field = value.field

        # =====================================
        # VALUE
        # =====================================

        if value.value_json is not None:

            final_value = value.value_json




        elif field.field_type == field.FIELD_FILE:

            files = [
                {
                    "url": (
                        f"{settings.BACKEND_URL}"
                        f"{item.file.url}"
                    ),
                    "name": item.original_name,
                }
                for item in value.files.all()
                if item.file
            ]

            final_value = files

        else:
            final_value = value.value_text

        # =====================================
        # OPTIONS
        # =====================================

        options = []

        if field.field_type in [
            field.FIELD_SELECT,
            field.FIELD_RADIO,
            field.FIELD_CHECKBOX,
        ]:
            options = [
                {
                    "label_ar": option.label_ar,
                    "label_en": option.label_en,
                    "value": option.value,
                }
                for option in (
                    field.options
                    .filter(is_active=True)
                    .order_by("order", "id")
                )
            ]

        # =====================================
        # SNAPSHOT
        # =====================================

        canonical_key = field.key

        display_value = final_value

        if field.system_key == "service_ids":
            display_value = resolve_service_groups(
                final_value
            )

        elif field.field_type in [
            field.FIELD_SELECT,
            field.FIELD_RADIO,
            field.FIELD_CHECKBOX,
        ]:
            selected_values = (
                final_value
                if isinstance(final_value, list)
                else [final_value]
            )

            labels = []

            for selected in selected_values:
                option = next(
                    (
                        opt
                        for opt in options
                        if opt["value"] == selected
                    ),
                    None,
                )

                labels.append(
                    option["label_ar"]
                    if option
                    else selected
                )

            display_value = (
                labels
                if isinstance(final_value, list)
                else labels[0]
                if labels
                else final_value
            )

        snapshot[canonical_key] = {
            "value": final_value,
            "display_value": display_value,
            "editable": (
                    (
                        not editable_form
                    )
                    or
                    (
                            field.key in editable_keys
                    )
            ),
            "field_key": field.key,
            "system_key": field.system_key,
            "field_type": field.field_type,
            "label_ar": field.label_ar,
            "label_en": field.label_en,
            "required": field.required,
            "options": options,
            "order": field.order,
            "section_order": field.section.order,
        }

    return snapshot
