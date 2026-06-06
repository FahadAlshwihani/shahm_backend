import json
import re
from django.utils import timezone

from django.utils.text import slugify
import mimetypes
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Prefetch
from rest_framework import serializers
from services.validators import (
    validate_uploaded_file,
)
from services.models import (
    AppointmentSlot,
    CareerJob,
    Service,
    MainService,
)
from .models import (
    FormTemplate,
    FormField,
    FormFieldOption,
    FormSubmission,
    FormSubmissionValue,
    FormSubmissionEditLog,
    FormSection,
    SuccessResponse,
    InfoModal,
    InfoModalSection,
)


class FormFieldOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFieldOption

        fields = [
            "id",
            "field",
            "label_ar",
            "label_en",
            "value",
            "order",
            "is_active",
        ]

        extra_kwargs = {
            "field": {"required": False},

            "value": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
        }

    def validate(self, attrs):
        label_ar = (
            attrs.get("label_ar", "")
            .strip()
        )

        label_en = (
            attrs.get("label_en", "")
            .strip()
        )

        if not label_ar and not label_en:
            raise serializers.ValidationError({
                "label_ar": (
                    "At least one label is required."
                )
            })

        return attrs


class FormFieldSerializer(serializers.ModelSerializer):
    key = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default="",
    )

    options = FormFieldOptionSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = FormField
        fields = [
            "id",
            "section",
            "field_type",
            "key",
            "system_key",
            "label_ar",
            "label_en",
            "placeholder_ar",
            "placeholder_en",
            "help_text_ar",
            "help_text_en",
            "required",
            "order",
            "width",
            "validation_rules",
            "settings",
            "options",
            "option_source",
            "dynamic_source",
        ]
        extra_kwargs = {
            "section": {"required": False},
            "key": {
                "required": False,
                "allow_blank": True,
                "allow_null": True,
            },
            "system_key": {
                "required": False,
                "allow_blank": True,
            },
        }

    def validate(self, attrs):
        instance = getattr(self, "instance", None)

        system_key = attrs.get(
            "system_key",
            getattr(instance, "system_key", ""),
        )

        key = attrs.get(
            "key",
            getattr(instance, "key", ""),
        )

        # system_key always overrides manual key
        normalized_key = ""

        if key:
            normalized_key = slugify(
                key,
                allow_unicode=False,
            ).replace("-", "_")

        elif system_key:
            normalized_key = slugify(
                system_key,
                allow_unicode=False,
            ).replace("-", "_")

        attrs["key"] = normalized_key

        # IMPORTANT:
        # if key is empty -> leave it empty
        # model.save() will generate unique key

        return attrs

    def create(self, validated_data):
        if not validated_data.get("key"):
            validated_data["key"] = None

        return super().create(validated_data)


class FormSectionSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)

    class Meta:
        model = FormSection
        fields = [
            "id",
            "form",
            "title_ar",
            "title_en",
            "description_ar",
            "description_en",
            "order",
            "is_active",
            "fields",
        ]

        extra_kwargs = {
            "form": {"required": False},
        }


class SuccessResponseSerializer(serializers.ModelSerializer):
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = SuccessResponse
        fields = [
            "id",
            "slug",
            "logo",
            "logo_url",
            "title_ar",
            "title_en",
            "subtitle_ar",
            "subtitle_en",
            "description_ar",
            "description_en",
            "show_reference_number",
            "reference_prefix",
            "button_label_ar",
            "button_label_en",
            "button_action_type",
            "button_url",
        ]

    def get_logo_url(self, obj):
        if not obj.logo:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.logo.url)

        return obj.logo.url

    def validate_button_url(self, value):

        if value and not (
                value.startswith("http://")
                or value.startswith("https://")
                or value.startswith("/")
        ):
            raise serializers.ValidationError(
                "Invalid button URL."
            )

        return value


class InfoModalSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfoModalSection
        fields = [
            "id",
            "modal",
            "title_ar",
            "title_en",
            "subtitle_ar",
            "subtitle_en",
            "body_ar",
            "body_en",
            "order",
            "is_active",
        ]
        extra_kwargs = {
            "modal": {"required": False},
        }


class InfoModalSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()

    class Meta:
        model = InfoModal
        fields = [
            "id",
            "slug",
            "title_ar",
            "title_en",
            "subtitle_ar",
            "subtitle_en",
            "description_ar",
            "description_en",
            "is_active",
            "sections",
        ]

    def get_sections(self, obj):
        qs = obj.sections.filter(is_active=True).order_by("order", "id")
        return InfoModalSectionSerializer(qs, many=True).data


class FormTemplateAdminSerializer(serializers.ModelSerializer):
    sections = FormSectionSerializer(many=True, read_only=True)
    submissions_count = serializers.IntegerField(read_only=True)

    success_response = SuccessResponseSerializer(read_only=True)

    success_response_id = serializers.PrimaryKeyRelatedField(
        source="success_response",
        queryset=SuccessResponse.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    def validate_email_field_key(self, value):
        if not value:
            return value

        instance = getattr(self, "instance", None)

        if not instance:
            return value

        exists = FormField.objects.filter(
            section__form=instance,
            key=value,
            field_type=FormField.FIELD_EMAIL,
            is_active=True,
        ).exists()

        if not exists:
            raise serializers.ValidationError(
                "Selected email field does not exist or is not an email field."
            )

        return value

    class Meta:
        model = FormTemplate
        fields = [
            "id",
            "title_ar",
            "title_en",
            "description_ar",
            "description_en",
            "slug",
            "submit_button_text_ar",
            "submit_button_text_en",
            "success_response",
            "success_response_id",
            "is_active",
            "requires_login",
            "requires_verification",
            "allow_multiple_submissions",
            "context_type",
            "form_type",
            "terms_text_ar",
            "terms_text_ar",
            "terms_text_en",
            "require_terms_approval",
            "created_by",
            "created_at",
            "updated_at",
            "sections",
            "submissions_count",
            "email_field_key",
            "allow_public_edit",
            "allow_admin_edit",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]


class FormTemplatePublicSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()
    success_response = SuccessResponseSerializer(read_only=True)

    success_response_id = serializers.PrimaryKeyRelatedField(
        source="success_response",
        queryset=SuccessResponse.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = FormTemplate
        fields = [
            "id",
            "title_ar",
            "title_en",
            "description_ar",
            "description_en",
            "slug",
            "context_type",
            "form_type",
            "terms_text_ar",
            "terms_text_ar",
            "terms_text_en",
            "require_terms_approval",
            "submit_button_text_ar",
            "submit_button_text_en",
            "success_response",
            "success_response_id",
            "requires_login",
            "requires_verification",
            "sections",
        ]

    def get_sections(self, obj):
        sections = obj.sections.filter(is_active=True).order_by("order", "id")

        return PublicFormSectionSerializer(
            sections,
            many=True,
            context=self.context,
        ).data


class PublicFormFieldOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFieldOption
        fields = [
            "id",
            "label_ar",
            "label_en",
            "value",
            "order",
        ]


class PublicFormFieldSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = FormField
        fields = [
            "id",
            "field_type",
            "key",
            "system_key",
            "label_ar",
            "label_en",
            "placeholder_ar",
            "placeholder_en",
            "help_text_ar",
            "help_text_en",
            "required",
            "order",
            "width",
            "validation_rules",
            "settings",
            "options",
            "option_source",
            "dynamic_source",
        ]

    def get_options(self, obj):
        if obj.option_source == FormField.SOURCE_DYNAMIC:
            if obj.dynamic_source == "appointment_slots":

                request = self.context.get("request")

                selected_period = None

                if request:
                    selected_period = request.query_params.get(
                        "appointment_period"
                    )

                slots = AppointmentSlot.objects.filter(
                    date__gte=timezone.localdate(),
                    is_available=True,
                )

                if selected_period:
                    slots = slots.filter(
                        shift=selected_period
                    )

                slots = slots.order_by(
                    "date",
                    "start_time",
                )
                slots = (
                    AppointmentSlot.objects
                    .filter(
                        date__gte=timezone.localdate(),
                    )
                    .order_by("date", "start_time")
                )

                return [
                    {
                        "id": slot.id,

                        "label_ar": (
                            f"{slot.start_time.strftime('%I:%M %p')}"
                        ),

                        "label_en": (
                            f"{slot.start_time.strftime('%I:%M %p')}"
                        ),

                        "full_label_ar": (
                            f"{slot.date} | "
                            f"{slot.start_time.strftime('%I:%M %p')} - "
                            f"{slot.end_time.strftime('%I:%M %p')}"
                        ),

                        "full_label_en": (
                            f"{slot.date} | "
                            f"{slot.start_time.strftime('%I:%M %p')} - "
                            f"{slot.end_time.strftime('%I:%M %p')}"
                        ),

                        "start_time": (
                            slot.start_time.strftime('%I:%M %p')
                        ),

                        "end_time": (
                            slot.end_time.strftime('%I:%M %p')
                        ),

                        "date": str(slot.date),

                        "is_available": slot.is_available,

                        "value": str(slot.id),

                        "order": index,
                    }
                    for index, slot in enumerate(slots)
                ]

            if obj.dynamic_source == "career_jobs":
                jobs = CareerJob.objects.filter(is_active=True).order_by("order", "id")

                return [
                    {
                        "id": job.id,
                        "label_ar": job.title_ar,
                        "label_en": job.title_en,
                        "value": str(job.id),
                        "order": index,
                    }
                    for index, job in enumerate(jobs)
                ]

            if obj.dynamic_source == "service_categories":
                categories = (
                    MainService.objects
                    .filter(is_active=True)
                    .order_by("order", "id")
                )
                return [
                    {
                        "id": category.id,
                        "label_ar": category.title_ar,
                        "label_en": category.title_en,
                        "value": str(category.id),
                        "order": index,
                    }
                    for index, category in enumerate(categories)
                ]

            if obj.dynamic_source == "services":
                services = (
                    Service.objects
                    .filter(is_active=True)
                    .order_by("order", "id")
                )

                return [
                    {
                        "id": service.id,
                        "label_ar": service.title_ar,
                        "label_en": service.title_en,
                        "value": str(service.id),
                        "order": index,
                    }
                    for index, service in enumerate(services)
                ]

        options = (
            obj.options
            .filter(is_active=True)
            .order_by("order", "id")
        )

        return PublicFormFieldOptionSerializer(options, many=True).data


class FormSubmissionValueSerializer(serializers.ModelSerializer):
    field_key = serializers.CharField(source="field.key", read_only=True)
    field_label_ar = serializers.CharField(source="field.label_ar", read_only=True)
    field_label_en = serializers.CharField(source="field.label_en", read_only=True)
    field_type = serializers.CharField(source="field.field_type", read_only=True)
    value_file_url = serializers.SerializerMethodField()

    class Meta:
        model = FormSubmissionValue
        fields = [
            "id",
            "field",
            "field_key",
            "field_label_ar",
            "field_label_en",
            "field_type",
            "value_text",
            "value_json",
            "value_file",
            "value_file_url",
        ]

    def get_value_file_url(self, obj):
        if not (
                obj.value_file
                and getattr(obj.value_file, "name", None)
        ):
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.value_file.url)

        return obj.value_file.url


class FormSubmissionAdminSerializer(serializers.ModelSerializer):
    form_title_ar = serializers.CharField(source="form.title_ar", read_only=True)
    form_title_en = serializers.CharField(source="form.title_en", read_only=True)
    values = FormSubmissionValueSerializer(many=True, read_only=True)

    class Meta:
        model = FormSubmission
        fields = [
            "id",
            "form",
            "form_title_ar",
            "form_title_en",
            "submitted_by",
            "status",
            "ip_address",
            "user_agent",
            "submitted_at",
            "values",
            "public_reference",
            "updated_at",
        ]


class FormSubmissionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormSubmission
        fields = ["status"]


class PublicFormSubmitSerializer(serializers.Serializer):
    data = serializers.JSONField(required=False)

    def _get_payload_data(self):
        request = self.context["request"]

        if request.content_type and request.content_type.startswith("multipart/form-data"):
            raw_data = request.data.get("data", "{}")

            if isinstance(raw_data, str):
                try:
                    return json.loads(raw_data)
                except json.JSONDecodeError:
                    raise serializers.ValidationError({
                        "data": "Invalid JSON in multipart data field."
                    })

            if isinstance(raw_data, dict):
                return raw_data

            return {}

        return request.data

    def validate(self, attrs):
        form = self.context["form"]
        request = self.context["request"]
        payload = self._get_payload_data()

        files = request.FILES

        if not isinstance(payload, dict):
            raise serializers.ValidationError("Submission payload must be an object.")

        fields = list(
            FormField.objects.filter(
                section__form=form,
                section__is_active=True,
                is_active=True,
            )
            .select_related("section")
            .prefetch_related("options")
            .order_by("section__order", "order", "id")
        )

        errors = {}
        cleaned_values = []

        if form.require_terms_approval:
            accepted = payload.get("accept_terms")

            if accepted is not True:
                errors["accept_terms"] = (
                    "Terms approval is required."
                )

        for field in fields:
            value = payload.get(field.key)
            uploaded_file = files.get(field.key)

            if field.field_type == FormField.FIELD_FILE:
                if field.required and not uploaded_file:
                    errors[field.key] = "This file is required."
                    continue

                if uploaded_file:
                    self._validate_file(field, uploaded_file)
                    cleaned_values.append({
                        "field": field,
                        "value_text": "",
                        "value_json": None,
                        "value_file": uploaded_file,
                    })

                continue

            if field.required and self._is_empty(value):
                errors[field.key] = "This field is required."
                continue

            if self._is_empty(value):
                cleaned_values.append({
                    "field": field,
                    "value_text": "",
                    "value_json": None,
                    "value_file": None,
                })
                continue

            try:
                normalized = self._validate_value(field, value)
            except serializers.ValidationError as exc:
                errors[field.key] = exc.detail
                continue

            if isinstance(normalized, (list, dict)):
                cleaned_values.append({
                    "field": field,
                    "value_text": "",
                    "value_json": normalized,
                    "value_file": None,
                })
            else:
                cleaned_values.append({
                    "field": field,
                    "value_text": str(normalized),
                    "value_json": None,
                    "value_file": None,
                })

        if errors:
            raise serializers.ValidationError(errors)

        attrs["cleaned_values"] = cleaned_values
        return attrs

    def save(self, **kwargs):
        form = self.context["form"]
        request = self.context["request"]

        user = request.user if request.user and request.user.is_authenticated else None

        with transaction.atomic():
            submission = FormSubmission.objects.create(
                form=form,
                submitted_by=user,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            values = []

            for item in self.validated_data["cleaned_values"]:
                values.append(FormSubmissionValue(
                    submission=submission,
                    field=item["field"],
                    value_text=item["value_text"],
                    value_json=item["value_json"],
                    value_file=item["value_file"],
                ))

            FormSubmissionValue.objects.bulk_create(values)

        return submission

    def _is_empty(self, value):
        return value is None or value == "" or value == [] or value == {}

    def _validate_value(self, field, value):
        rules = field.validation_rules or {}

        if field.field_type == FormField.FIELD_HIDDEN:
            return str(value).strip()

        if field.field_type == FormField.FIELD_PHONE:

            if not isinstance(value, dict):
                raise serializers.ValidationError(
                    "Phone field must be an object."
                )

            country_code = str(
                value.get("country_code", "")
            ).strip()

            number = str(
                value.get("number", "")
            ).strip()

            full_phone = f"{country_code}{number}"

            if not re.match(
                    r"^[0-9+\-\s()]{7,25}$",
                    full_phone,
            ):
                raise serializers.ValidationError(
                    "Invalid phone number."
                )

            return {
                "country_code": country_code,
                "number": number,
            }

        if field.field_type in [
            FormField.FIELD_TEXT,
            FormField.FIELD_TEXTAREA,
        ]:
            value = str(value).strip()

            min_length = rules.get("min_length")
            max_length = rules.get("max_length")

            if min_length is not None and len(value) < int(min_length):
                raise serializers.ValidationError(
                    f"Minimum length is {min_length}."
                )

            if max_length is not None and len(value) > int(max_length):
                raise serializers.ValidationError(
                    f"Maximum length is {max_length}."
                )

            return value

        if field.field_type == FormField.FIELD_EMAIL:
            value = str(value).strip()
            try:
                validate_email(value)
            except DjangoValidationError:
                raise serializers.ValidationError("Invalid email address.")
            return value

        if field.field_type == FormField.FIELD_NUMBER:
            try:
                number = float(value)
            except (TypeError, ValueError):
                raise serializers.ValidationError("Invalid number.")

            min_value = rules.get("min")
            max_value = rules.get("max")

            if min_value is not None and number < float(min_value):
                raise serializers.ValidationError(f"Minimum value is {min_value}.")

            if max_value is not None and number > float(max_value):
                raise serializers.ValidationError(f"Maximum value is {max_value}.")

            return number

        if field.field_type == FormField.FIELD_DATE:
            value = str(value).strip()
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD.")
            return value

        if field.field_type in [
            FormField.FIELD_SELECT,
            FormField.FIELD_RADIO,
        ]:

            # =====================================================
            # DYNAMIC SERVICES
            # =====================================================

            if (
                    field.option_source == FormField.SOURCE_DYNAMIC
                    and field.dynamic_source == "services"
            ):

                if not isinstance(value, list):
                    raise serializers.ValidationError(
                        "Services value must be a list."
                    )

                normalized_groups = []

                valid_main_services = set(
                    MainService.objects.filter(
                        is_active=True
                    ).values_list("id", flat=True)
                )

                valid_services = {
                    service.id: service.main_service_id
                    for service in Service.objects.filter(
                        is_active=True
                    ).only("id", "main_service_id")
                }

                for group in value:

                    if not isinstance(group, dict):
                        raise serializers.ValidationError(
                            "Invalid services structure."
                        )

                    main_service = group.get(
                        "main_service"
                    )

                    services = group.get(
                        "services",
                        [],
                    )

                    try:
                        main_service = int(main_service)

                    except (
                            TypeError,
                            ValueError,
                    ):
                        raise serializers.ValidationError(
                            "Invalid main service."
                        )

                    if (
                            main_service
                            not in valid_main_services
                    ):
                        raise serializers.ValidationError(
                            "Invalid main service."
                        )

                    if not isinstance(
                            services,
                            list,
                    ):
                        raise serializers.ValidationError(
                            "Services must be a list."
                        )

                    normalized_services = []

                    for service_id in services:

                        try:
                            service_id = int(service_id)

                        except (
                                TypeError,
                                ValueError,
                        ):
                            raise serializers.ValidationError(
                                "Invalid service selected."
                            )

                        if service_id not in valid_services:
                            raise serializers.ValidationError(
                                "Invalid service selected."
                            )

                        if valid_services[service_id] != main_service:
                            raise serializers.ValidationError(
                                "Service does not belong to selected main service."
                            )

                        normalized_services.append(
                            str(service_id)
                        )

                    normalized_groups.append({
                        "main_service": str(
                            main_service
                        ),
                        "services": normalized_services,
                    })

                return normalized_groups

            # =====================================================
            # OTHER DYNAMIC SOURCES
            # =====================================================

            value = str(value).strip()

            if field.option_source == FormField.SOURCE_DYNAMIC:

                if obj.dynamic_source == "appointment_periods":
                    return [
                        {
                            "id": "morning",
                            "label_ar": "الفترة الصباحية",
                            "label_en": "Morning",
                            "value": "morning",
                            "order": 0,
                        },
                        {
                            "id": "evening",
                            "label_ar": "الفترة المسائية",
                            "label_en": "Evening",
                            "value": "evening",
                            "order": 1,
                        },
                    ]

                if field.dynamic_source == "appointment_slots":

                    exists = AppointmentSlot.objects.filter(
                        id=value,
                        is_available=True,
                        date__gte=timezone.localdate(),
                    ).exists()

                    if not exists:
                        raise serializers.ValidationError(
                            "Selected slot is not available."
                        )

                    return value

                if field.dynamic_source == "career_jobs":

                    exists = CareerJob.objects.filter(
                        id=value,
                        is_active=True,
                    ).exists()

                    if not exists:
                        raise serializers.ValidationError(
                            "Selected job is invalid."
                        )

                    return value

                if field.dynamic_source == "service_categories":

                    exists = MainService.objects.filter(
                        id=value,
                        is_active=True,
                    ).exists()

                    if not exists:
                        raise serializers.ValidationError(
                            "Selected service category is invalid."
                        )

                    return value

                if field.dynamic_source == "appointment_periods":
                    allowed = {"morning", "evening"}

                    if value not in allowed:
                        raise serializers.ValidationError(
                            "Invalid appointment period."
                        )

                    return value

                raise serializers.ValidationError(
                    "Invalid dynamic source."
                )

            # =====================================================
            # STATIC OPTIONS
            # =====================================================

            allowed = set(
                field.options
                .filter(is_active=True)
                .values_list("value", flat=True)
            )

            if value not in allowed:
                raise serializers.ValidationError(
                    "Invalid selected option."
                )

            return value

        if field.field_type == FormField.FIELD_CHECKBOX:

            if isinstance(value, bool):
                return value

            if not isinstance(value, list):
                raise serializers.ValidationError(
                    "Checkbox value must be boolean or list."
                )

            # =====================================================
            # DYNAMIC SERVICES VALIDATION
            # =====================================================
            if (
                    field.option_source == FormField.SOURCE_DYNAMIC
                    and field.dynamic_source == "services"
            ):
                try:
                    normalized_ids = [
                        int(item)
                        for item in value
                    ]
                except (TypeError, ValueError):
                    raise serializers.ValidationError(
                        "Invalid services selected."
                    )

                valid_ids = set(
                    Service.objects.filter(
                        is_active=True
                    ).values_list("id", flat=True)
                )

                invalid_ids = [
                    item
                    for item in normalized_ids
                    if item not in valid_ids
                ]

                if invalid_ids:
                    raise serializers.ValidationError(
                        "Invalid services selected."
                    )

                return [
                    str(item)
                    for item in normalized_ids
                ]

            # =====================================================
            # STATIC OPTIONS VALIDATION
            # =====================================================
            allowed = set(
                field.options
                .filter(is_active=True)
                .values_list("value", flat=True)
            )

            if allowed:
                invalid = [
                    item
                    for item in value
                    if item not in allowed
                ]

                if invalid:
                    raise serializers.ValidationError(
                        "Invalid checkbox option."
                    )

            return value

        return value

    def _validate_file(
            self,
            field,
            uploaded_file,
    ):
        rules = field.validation_rules or {}

        validate_uploaded_file(
            uploaded_file=uploaded_file,
            allowed_extensions=rules.get(
                "allowed_extensions",
                [],
            ),
            max_size_mb=int(
                rules.get("max_size_mb", 10)
            ),
        )

    def _get_client_ip(self, request):
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class PublicFormSectionSerializer(serializers.ModelSerializer):
    fields = serializers.SerializerMethodField(
        method_name="get_section_fields"
    )

    class Meta:
        model = FormSection
        fields = [
            "id",
            "title_ar",
            "title_en",
            "description_ar",
            "description_en",
            "order",
            "fields",
        ]

    def get_section_fields(self, obj):
        fields = (
            obj.fields
            .filter(is_active=True)
            .prefetch_related("options")
            .order_by("order", "id")
        )

        return PublicFormFieldSerializer(
            fields,
            many=True,
            context=self.context,
        ).data


class SubmissionPrefillSerializer(serializers.Serializer):
    field_key = serializers.CharField()
    value = serializers.JSONField()


class PublicSubmissionUpdateSerializer(serializers.Serializer):
    data = serializers.JSONField(required=False)

    def _get_payload_data(self):
        request = self.context["request"]

        if (
                request.content_type
                and request.content_type.startswith("multipart/form-data")
        ):
            raw_data = request.data.get("data", "{}")

            if isinstance(raw_data, str):
                try:
                    return json.loads(raw_data)
                except json.JSONDecodeError:
                    raise serializers.ValidationError({
                        "data": "Invalid JSON payload."
                    })

            if isinstance(raw_data, dict):
                return raw_data

            return {}

        return request.data

    def validate(self, attrs):

        form = self.context["form"]
        submission = self.context["submission"]
        request = self.context["request"]

        payload = self._get_payload_data()
        files = request.FILES

        fields = list(
            FormField.objects.filter(
                section__form=form,
                section__is_active=True,
                is_active=True,
                allow_public_edit=True,
            )
            .select_related("section")
            .prefetch_related("options")
        )

        existing_values = {
            item.field_id: item
            for item in submission.values.select_related("field")
        }

        cleaned_values = []
        errors = {}

        for field in fields:

            incoming_value = payload.get(field.key, None)
            uploaded_file = files.get(field.key)

            existing = existing_values.get(field.id)

            # FILES
            if field.field_type == FormField.FIELD_FILE:

                if uploaded_file:
                    validate_uploaded_file(
                        uploaded_file=uploaded_file,
                        allowed_extensions=(
                                field.validation_rules or {}
                        ).get("allowed_extensions", []),
                        max_size_mb=int(
                            (field.validation_rules or {}).get(
                                "max_size_mb",
                                10,
                            )
                        ),
                    )

                    cleaned_values.append({
                        "field": field,
                        "value_text": "",
                        "value_json": None,
                        "value_file": uploaded_file,
                        "existing": existing,
                    })

                continue

            # NOT SENT
            if incoming_value is None:
                continue

            validator = PublicFormSubmitSerializer(
                context=self.context
            )

            try:
                normalized = validator._validate_value(
                    field,
                    incoming_value,
                )
            except serializers.ValidationError as exc:
                errors[field.key] = exc.detail
                continue

            cleaned_values.append({
                "field": field,
                "value_text": (
                    ""
                    if isinstance(normalized, (list, dict))
                    else str(normalized)
                ),
                "value_json": (
                    normalized
                    if isinstance(normalized, (list, dict))
                    else None
                ),
                "value_file": None,
                "existing": existing,
            })

        if errors:
            raise serializers.ValidationError(errors)

        attrs["cleaned_values"] = cleaned_values

        return attrs

    @transaction.atomic
    def save(self, **kwargs):

        submission = self.context["submission"]
        request = self.context["request"]

        for item in self.validated_data["cleaned_values"]:

            field = item["field"]
            existing = item["existing"]

            old_value = None

            if existing:
                if existing.value_json is not None:
                    old_value = existing.value_json
                elif existing.value_file:
                    old_value = existing.value_file.url
                else:
                    old_value = existing.value_text

            new_value = (
                    item["value_json"]
                    or item["value_text"]
                    or (
                        item["value_file"].name
                        if item["value_file"]
                        else None
                    )
            )

            if existing:

                existing.value_text = item["value_text"]
                existing.value_json = item["value_json"]

                if item["value_file"]:
                    existing.value_file = item["value_file"]

                existing.save()

            else:

                FormSubmissionValue.objects.create(
                    submission=submission,
                    field=field,
                    value_text=item["value_text"],
                    value_json=item["value_json"],
                    value_file=item["value_file"],
                )

            FormSubmissionEditLog.objects.create(
                submission=submission,
                edited_by_admin=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
                field_key=field.key,
                old_value=old_value,
                new_value=new_value,
            )

        submission.save(update_fields=["updated_at"])

        return submission


def build_submission_prefill(submission):
    values = {}

    for item in (
            submission.values
                    .select_related("field")
                    .all()
    ):

        field_key = item.field.key

        if item.value_json is not None:
            final_value = item.value_json

        elif item.value_file and getattr(item.value_file, "name", None):
            final_value = item.value_file.url

        else:
            final_value = item.value_text

        values[field_key] = final_value

    return values
