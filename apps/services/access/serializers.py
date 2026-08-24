from rest_framework import serializers
from django.utils import timezone
from .activity import (
    AccessActivityService,
)
from apps.services.models import (
    ServiceRequestAccessLink,
)

from apps.form_builder.models import (
    FormTemplate,
    FormField,

)

from django.conf import settings
from apps.services.request_otp import (
    ServiceRequestOTP,
)


class SendOTPSerializer(serializers.Serializer):
    public_key = serializers.CharField()


class VerifyOTPSerializer(serializers.Serializer):
    public_key = serializers.CharField()

    code = serializers.CharField(
        min_length=6,
        max_length=6,
    )

    def validate(self, attrs):

        try:
            link = ServiceRequestAccessLink.objects.get(
                public_key=attrs["public_key"]
            )

        except ServiceRequestAccessLink.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "detail": "Invalid access link."
                }
            )

        otp = (
            ServiceRequestOTP.objects
            .filter(
                link=link,
                is_verified=False,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp:
            raise serializers.ValidationError(
                {
                    "detail": "OTP not found."
                }
            )

        if timezone.now() > otp.expires_at:
            raise serializers.ValidationError(
                {
                    "detail": "OTP expired."
                }
            )

        otp.attempts += 1
        otp.save(update_fields=["attempts"])

        if otp.attempts >= 5:
            raise serializers.ValidationError(
                {
                    "detail": "Too many attempts."
                }
            )

        if not otp.verify_code(attrs["code"]):

            request = self.context.get(
                "request"
            )

            if request:
                AccessActivityService.log(
                    request=request,
                    link=link,
                    action="otp_failed",
                )

            raise serializers.ValidationError(
                {
                    "detail": "Invalid OTP."
                }
            )

        attrs["otp"] = otp
        attrs["link"] = link

        return attrs


class CreateAccessLinkSerializer(
    serializers.Serializer
):
    form_id = serializers.IntegerField(
        write_only=True,
    )

    editable_fields = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        default=list,
    )

    selected_form = serializers.SerializerMethodField()

    form_title_ar = serializers.CharField(
        source="form.title_ar",
        read_only=True,
    )

    form_title_en = serializers.CharField(
        source="form.title_en",
        read_only=True,
    )

    expires_in_hours = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=720,
        default=72,
    )

    max_edits = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=50,
        default=3,
    )

    def validate_editable_fields(
            self,
            value,
    ):
        form_id = self.initial_data.get(
            "form_id"
        )

        if not form_id:
            return value

        form = (
            FormTemplate.objects
            .filter(pk=form_id)
            .first()
        )

        if not form:
            return value

        allowed_keys = set(
            FormField.objects.filter(
                section__form=form,
                is_active=True,
                section__is_active=True,
            ).values_list(
                "key",
                flat=True,
            )
        )

        invalid_keys = [
            key
            for key in value
            if key not in allowed_keys
        ]

        if invalid_keys:
            raise serializers.ValidationError(
                f"Invalid field keys: {invalid_keys}"
            )

        return value


class AccessLinkSerializer(serializers.ModelSerializer):
    access_url = serializers.SerializerMethodField()
    selected_form = serializers.SerializerMethodField()

    form_id = serializers.SerializerMethodField()
    form_title_ar = serializers.SerializerMethodField()
    form_title_en = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequestAccessLink

        fields = [
            "id",
            "public_key",
            "status",
            "edit_count",
            "max_edits",
            "verified_at",
            "last_accessed_at",
            "expires_at",
            "created_at",
            "access_url",
            "editable_fields",

            # form info
            "form_id",
            "form_title_ar",
            "form_title_en",
            "selected_form",
        ]

    def get_access_url(self, obj):

        frontend_url = (
            getattr(
                settings,
                "FRONTEND_URL",
                "",
            )
            .rstrip("/")
        )

        return (
            f"{frontend_url}"
            f"/request-access/"
            f"{obj.public_key}/"
        )

    def get_selected_form(self, obj):

        if not obj.form:
            return None

        return {
            "id": obj.form.id,
            "title_ar": obj.form.title_ar,
            "title_en": obj.form.title_en,
        }

    def get_form_id(self, obj):

        if not obj.form:
            return None

        return obj.form.id

    def get_form_title_ar(self, obj):

        if not obj.form:
            return None

        return obj.form.title_ar

    def get_form_title_en(self, obj):

        if not obj.form:
            return None

        return obj.form.title_en
