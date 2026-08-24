from rest_framework import serializers
from apps.form_builder.models import FormTemplate

from .access.snapshot import (
    build_submission_snapshot,
)

from .access.serializers import (
    AccessLinkSerializer,
)

from .models import (
    Service,
    ServiceAdvisoryPage,
    ServiceAdvisoryRequest,
    CareerJob,
    CareerApplication,
    ServiceAdvisoryRequestItem,
    MainService,
    ServiceSection,
    ServicePageCMS,
    ServiceAdvisoryRequestFile,
)
from .client_files import Client, ClientFile
from apps.services.utils.references import (
    generate_reference,
)


class MainServiceSerializer(serializers.ModelSerializer):
    services_count = serializers.SerializerMethodField()

    class Meta:
        model = MainService
        fields = "__all__"

    def get_services_count(self, obj):
        return obj.services.filter(
            is_active=True
        ).count()


class ServiceSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceSection
        fields = "__all__"


class FormTemplateMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormTemplate
        fields = [
            "id",
            "title_ar",
            "title_en",
            "slug",
        ]


class ServiceSerializer(serializers.ModelSerializer):
    sections = ServiceSectionSerializer(
        many=True,
        read_only=True,
    )

    main_service_data = MainServiceSerializer(
        source="main_service",
        read_only=True,
    )

    class Meta:
        model = Service
        fields = "__all__"
        read_only_fields = (
            "slug",
            "serial_number",
        )


class ServicePageCMSSerializer(serializers.ModelSerializer):
    primary_form_data = FormTemplateMiniSerializer(
        source="primary_form",
        read_only=True,
    )

    class Meta:
        model = ServicePageCMS

        fields = (
            "id",
            "hero_logo",
            "hero_media_type",
            "hero_image",
            "hero_video",
            "title_ar",
            "title_en",
            "description_ar",
            "description_en",
            "search_placeholder_ar",
            "search_placeholder_en",

            "primary_button_label_ar",
            "primary_button_label_en",
            "primary_action_type",
            "primary_url",
            "primary_form",
            "primary_form_data",

            "is_active",
            "updated_at",
        )


class ServiceAdvisoryPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAdvisoryPage
        fields = "__all__"


class ServiceMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ["id", "title_ar", "title_en"]


class ServiceAdvisoryRequestItemSerializer(serializers.ModelSerializer):
    service = ServiceMiniSerializer(read_only=True)

    class Meta:
        model = ServiceAdvisoryRequestItem
        fields = ["service"]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"


class ClientFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientFile
        fields = "__all__"


class ServiceAdvisoryRequestFileSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = ServiceAdvisoryRequestFile
        fields = [
            "id",
            "file",
            "file_type",
            "original_field_key",
            "uploaded_at",
        ]


# =========================================================
# ================= CAREERS SERIALIZERS ===================
# =========================================================

class CareerJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerJob
        fields = "__all__"


class CareerApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(
        source="job.title_ar",
        read_only=True,
    )
    dynamic_fields = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()
    form_submission_id = serializers.IntegerField(
        source="form_submission.id",
        read_only=True,
    )
    form_id = serializers.IntegerField(
        source="form_submission.form.id",
        read_only=True,
    )
    form_title_ar = serializers.CharField(
        source="form_submission.form.title_ar",
        read_only=True,
    )
    form_title_en = serializers.CharField(
        source="form_submission.form.title_en",
        read_only=True,
    )

    class Meta:
        model = CareerApplication
        fields = [
            "id",
            "job",
            "job_title",
            "reference",
            "status",
            "created_at",
            "form_submission_id",
            "form_id",
            "form_title_ar",
            "form_title_en",
            "files",
            "dynamic_fields",
        ]
        read_only_fields = [
            "reference",
            "created_at",
        ]

    def get_dynamic_fields(self, obj):
        if not obj.form_submission:
            return []

        request = self.context.get("request")

        values = (
            obj.form_submission.values
            .select_related("field")
            .all()
        )

        result = []

        for value in values:
            field = value.field

            if value.value_json is not None:
                field_value = value.value_json
            elif value.value_file and getattr(value.value_file, "name", None):
                field_value = (
                    request.build_absolute_uri(value.value_file.url)
                    if request
                    else value.value_file.url
                )
            else:
                field_value = value.value_text

            options = []
            display_value = field_value

            if field.field_type in [
                "select",
                "radio",
                "checkbox",
            ]:
                options = [
                    {
                        "value": o.value,
                        "label_ar": o.label_ar,
                        "label_en": o.label_en,
                    }
                    for o in field.options.all()
                ]

                selected = (
                    field_value
                    if isinstance(field_value, list)
                    else [field_value]
                )

                labels = []

                for selected_value in selected:
                    match = next(
                        (
                            opt
                            for opt in options
                            if opt["value"] == selected_value
                        ),
                        None,
                    )

                    labels.append(
                        match["label_ar"]
                        if match
                        else selected_value
                    )

                display_value = (
                    labels
                    if isinstance(field_value, list)
                    else labels[0] if labels else field_value
                )

            result.append({
                "field_id": field.id,
                "key": field.key,
                "system_key": field.system_key,
                "label_ar": field.label_ar,
                "label_en": field.label_en,
                "field_type": field.field_type,
                "value": field_value,
                "display_value": display_value,
                "options": options,
                "required": field.required,
            })
        return result

    def get_files(self, obj):
        if not obj.form_submission:
            return []

        request = self.context.get("request")
        result = []

        values = (
            obj.form_submission.values
            .select_related("field")
            .all()
        )

        for value in values:
            if not (
                    value.value_file
                    and getattr(value.value_file, "name", None)
            ):
                continue

            file_url = value.value_file.url

            if request:
                file_url = request.build_absolute_uri(file_url)

            result.append({
                "field_id": value.field.id,
                "key": value.field.key,
                "system_key": value.field.system_key,
                "label_ar": value.field.label_ar,
                "label_en": value.field.label_en,
                "field_type": value.field.field_type,
                "file_url": file_url,
            })

        return result


class ServiceAdvisoryRequestSerializer(serializers.ModelSerializer):
    items = ServiceAdvisoryRequestItemSerializer(
        many=True,
        read_only=True,
    )

    dynamic_fields = serializers.SerializerMethodField()

    service_ids = serializers.JSONField(
        write_only=True,
        required=False,
    )

    form_submission_id = serializers.IntegerField(
        source="form_submission.id",
        read_only=True,
    )

    form_id = serializers.IntegerField(
        source="form_submission.form.id",
        read_only=True,
    )

    form_title_ar = serializers.CharField(
        source="form_submission.form.title_ar",
        read_only=True,
    )

    form_title_en = serializers.CharField(
        source="form_submission.form.title_en",
        read_only=True,
    )

    snapshot = serializers.SerializerMethodField()
    access_links = serializers.SerializerMethodField()

    files = ServiceAdvisoryRequestFileSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = ServiceAdvisoryRequest
        fields = [
            "id",
            "title",
            "first_name",
            "last_name",
            "reference",
            "email",
            "phone",
            "message",
            "files",
            "service_ids",
            "items",
            "status",
            "created_at",
            "form_submission_id",
            "form_id",
            "form_title_ar",
            "form_title_en",
            "snapshot",
            "dynamic_fields",
            "access_links",
        ]

    def get_snapshot(self, obj):
        if not obj.form_submission:
            return None

        from .access.snapshot import (
            build_submission_snapshot,
        )

        return build_submission_snapshot(
            obj.form_submission
        )

    def get_access_links(self, obj):
        from .access.serializers import (
            AccessLinkSerializer,
        )

        links = obj.access_links.all().order_by(
            "-created_at"
        )

        return AccessLinkSerializer(
            links,
            many=True,
            context=self.context,
        ).data

    def create(self, validated_data):
        service_ids = validated_data.pop(
            "service_ids",
            [],
        )

        obj = ServiceAdvisoryRequest.objects.create(
            **validated_data
        )

        for group in service_ids:

            services = group.get(
                "services",
                [],
            )

            for sid in services:
                ServiceAdvisoryRequestItem.objects.create(
                    request=obj,
                    service_id=sid,
                )

        obj.reference = generate_reference(
            "service"
        )

        obj.save(
            update_fields=[
                "reference",
            ]
        )

        return obj

    def get_dynamic_fields(self, obj):
        if not obj.form_submission:
            return []

        values = (
            obj.form_submission.values
            .select_related("field")
            .all()
        )

        result = []

        for value in values:
            field = value.field

            request = self.context.get("request")

            if value.value_json is not None:
                field_value = value.value_json


            elif value.value_file and getattr(value.value_file, "name", None):

                if request:

                    field_value = request.build_absolute_uri(

                        value.value_file.url

                    )

                else:

                    field_value = value.value_file.url

            else:
                field_value = value.value_text

            result.append({
                "field_id": field.id,
                "key": field.key,
                "system_key": field.system_key,
                "label_ar": field.label_ar,
                "label_en": field.label_en,
                "field_type": field.field_type,
                "value": field_value,
                "required": field.required,
            })

        return result
