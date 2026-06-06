from datetime import timedelta
import json
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework import status

from accounts.permissions import (
    IsEditorOrAbove,
)

from email_settings.services import (
    DynamicEmailService,
)

from services.models import (
    ServiceAdvisoryRequest,
    ServiceRequestAccessLink,
)

from services.request_otp import (
    ServiceRequestOTP,
)

from services.request_access import (
    ServiceRequestAccessSession,
    ServiceRequestAccessActivity,
)

from .utils.masking import mask_email

from .access_activity import (
    AccessActivityService,
)

from .access_serializers import (
    SendOTPSerializer,
    VerifyOTPSerializer,
    CreateAccessLinkSerializer,
    AccessLinkSerializer,
)

from .access_snapshot import (
    build_submission_snapshot,
)

from .access_security import (
    validate_access_link,
    validate_access_session,
)

from .access_update import (
    SubmissionUpdateService,
)

from .access_update_serializers import (
    EditableSubmissionUpdateSerializer,
)
from form_builder.models import (
    FormTemplate,
    FormSubmission,
    FormSection,
    FormField,
    FormSubmissionEditLog,
)


class SendOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "otp"

    RESEND_COOLDOWN_SECONDS = 60

    def post(self, request):
        serializer = SendOTPSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        public_key = serializer.validated_data[
            "public_key"
        ]

        link = get_object_or_404(
            ServiceRequestAccessLink.objects
            .select_related("request"),
            public_key=public_key,
        )

        validate_access_link(link)

        request_email = link.request.email

        recent_otp = (
            ServiceRequestOTP.objects
            .filter(
                link=link,
                created_at__gte=(
                        timezone.now()
                        - timedelta(
                    seconds=self.RESEND_COOLDOWN_SECONDS
                )
                ),
            )
            .exists()
        )

        if recent_otp:
            return Response(
                {
                    "detail": (
                        "Please wait before requesting another OTP."
                    )
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        otp_code = ServiceRequestOTP.generate_code()

        otp = ServiceRequestOTP.objects.create(
            link=link,
            email=link.request.email,
            expires_at=ServiceRequestOTP.expiry(),
        )

        otp.set_code(otp_code)
        otp.save(update_fields=["code"])

        DynamicEmailService.send_email(
            subject="Verification Code",
            body=(
                f"Your verification code is: {otp_code}"
            ),
            recipient_list=[
                request_email,
            ],
        )

        AccessActivityService.log(
            request=request,
            link=link,
            action="otp_sent",
        )

        return Response(
            {
                "success": True,
                "message": "OTP sent successfully.",
                "masked_destination": mask_email(request_email),
                "cooldown_seconds": self.RESEND_COOLDOWN_SECONDS,
            }
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "otp"

    def post(self, request):
        serializer = VerifyOTPSerializer(
            data=request.data,
            context={
                "request": request,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        otp = serializer.validated_data[
            "otp"
        ]

        link = serializer.validated_data[
            "link"
        ]

        otp.is_verified = True
        otp.save(
            update_fields=[
                "is_verified",
            ]
        )

        link.verified_at = timezone.now()
        link.last_accessed_at = timezone.now()

        link.save(
            update_fields=[
                "verified_at",
                "last_accessed_at",
            ]
        )

        session = (
            ServiceRequestAccessSession.objects
            .create(
                link=link,
                otp=otp,
                token=(
                    ServiceRequestAccessSession
                    .generate_token()
                ),
                expires_at=(
                        timezone.now()
                        + timedelta(minutes=10)
                ),
            )
        )

        AccessActivityService.log(
            request=request,
            link=link,
            action="otp_verified",
        )

        return Response(
            {
                "success": True,
                "access_token": session.token,
                "expires_at": session.expires_at,
            }
        )


class EditableSubmissionSnapshotView(APIView):
    permission_classes = [AllowAny]

    def get(
            self,
            request,
            public_key,
    ):
        link = get_object_or_404(
            ServiceRequestAccessLink.objects
            .select_related(
                "submission",
                "form",
            ),
            public_key=public_key,
        )

        validate_access_link(link)

        token = request.headers.get(
            "X-Access-Token"
        )

        validate_access_session(
            public_key=public_key,
            token=token,
        )

        # =================================================
        # CURRENT SUBMISSION VALUES
        # =================================================

        submission_values = {}

        values_queryset = (
            link.submission.values
            .select_related("field")
            .all()
        )

        for value in values_queryset:

            field = value.field

            field_key = field.key

            if value.value_json is not None:
                field_value = (
                    value.value_json
                )

            elif value.value_file:
                field_value = (
                    value.value_file.url
                )

            else:
                field_value = (
                    value.value_text
                )

            submission_values[
                field_key
            ] = field_value

        # =================================================
        # BUILD DYNAMIC FORM
        # =================================================

        editable_fields = (
                link.editable_fields
                or []
        )

        form_sections = []

        sections_queryset = (
            link.form.sections
            .filter(
                is_active=True,
            )
            .prefetch_related(
                "fields",
                "fields__options",
            )
            .order_by("order")
        )

        for section in sections_queryset:

            section_fields = []

            fields_queryset = (
                section.fields
                .filter(
                    is_active=True,
                )
                .order_by("order")
            )

            for field in fields_queryset:

                options = []

                if hasattr(
                        field,
                        "options",
                ):

                    for option in (
                            field.options.all()
                    ):
                        options.append({
                            "id": option.id,
                            "label_ar": getattr(
                                option,
                                "label_ar",
                                "",
                            ),
                            "label_en": getattr(
                                option,
                                "label_en",
                                "",
                            ),
                            "value": option.value,
                        })

                is_editable = (
                    True
                    if not editable_fields
                    else (
                            field.key in editable_fields
                    )
                )

                section_fields.append({
                    "id": field.id,
                    "key": field.key,
                    "system_key": (
                        field.system_key
                    ),
                    "editable": (
                        is_editable
                    ),
                    "field_type": (
                        field.field_type
                    ),
                    "label_ar": (
                        field.label_ar
                    ),
                    "label_en": (
                        field.label_en
                    ),
                    "placeholder_ar": (
                        field.placeholder_ar
                    ),
                    "placeholder_en": (
                        field.placeholder_en
                    ),
                    "help_text_ar": (
                        field.help_text_ar
                    ),
                    "help_text_en": (
                        field.help_text_en
                    ),
                    "required": (
                        field.required
                    ),
                    "width": (
                        field.width
                    ),
                    "order": (
                        field.order
                    ),
                    "options": options,
                    "dynamic_source": getattr(
                        field,
                        "dynamic_source",
                        None,
                    ),
                    "validation_rules": getattr(
                        field,
                        "validation_rules",
                        {},
                    ),
                })

            form_sections.append({
                "id": section.id,
                "title_ar": (
                    section.title_ar
                ),
                "title_en": (
                    section.title_en
                ),
                "description_ar": (
                    section.description_ar
                ),
                "description_en": (
                    section.description_en
                ),
                "order": (
                    section.order
                ),
                "fields": (
                    section_fields
                ),
            })

        # =================================================
        # UPDATE ACCESS TIME
        # =================================================

        link.last_accessed_at = (
            timezone.now()
        )

        link.save(
            update_fields=[
                "last_accessed_at",
            ]
        )

        # =================================================
        # LOG ACTIVITY
        # =================================================

        AccessActivityService.log(
            request=request,
            link=link,
            action="snapshot_viewed",
        )

        # =================================================
        # RESPONSE
        # =================================================

        return Response({
            "form": {
                "id": link.form.id,
                "title_ar": (
                    link.form.title_ar
                ),
                "title_en": (
                    link.form.title_en
                ),
                "description_ar": (
                    link.form.description_ar
                ),
                "description_en": (
                    link.form.description_en
                ),
                "sections": (
                    form_sections
                ),
            },
            "values": (
                submission_values
            ),
            "editable_fields": (
                editable_fields
            ),
            "edit_count": (
                link.edit_count
            ),
            "max_edits": (
                link.max_edits
            ),
            "expires_at": (
                link.expires_at
            ),
        })


import json


class EditableSubmissionUpdateView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, public_key):

        link = get_object_or_404(
            ServiceRequestAccessLink.objects
            .select_related(
                "submission",
            ),
            public_key=public_key,
        )

        validate_access_link(link)

        token = request.headers.get(
            "X-Access-Token"
        )

        validate_access_session(
            public_key=public_key,
            token=token,
        )

        # =========================================
        # NORMALIZE MULTIPART DATA
        # =========================================

        cleaned_data = {}

        for key in request.data.keys():

            uploaded_files = request.FILES.getlist(key)

            # FILE
            if uploaded_files:
                cleaned_data[key] = (
                    uploaded_files
                    if len(uploaded_files) > 1
                    else uploaded_files[0]
                )
                continue

            value = request.data.get(key)

            # JSON VALUES
            try:
                cleaned_data[key] = json.loads(value)
            except Exception:
                cleaned_data[key] = value

        print("=" * 50)
        print("REQUEST DATA:", request.data)
        print("FILES:", request.FILES)
        print("CLEANED DATA:", cleaned_data)
        print("LINK EDITABLE:", link.editable_fields)
        print("=" * 50)

        updated_fields = (
            SubmissionUpdateService
            .update_submission(
                submission=link.submission,
                cleaned_data=cleaned_data,
                editable_form=link.form,
                link=link,
            )
        )

        AccessActivityService.log(
            request=request,
            link=link,
            action="submission_updated",
            metadata={
                "updated_fields": updated_fields,
            },
        )

        return Response(
            {
                "success": True,
                "updated_fields": updated_fields,
            }
        )


class AdminCreateAccessLinkView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    def post(self, request, request_id):
        advisory_request = get_object_or_404(
            ServiceAdvisoryRequest.objects
            .select_related(
                "form_submission",
                "form_submission__form",
            ),
            pk=request_id,
        )

        if not advisory_request.form_submission:
            return Response(
                {
                    "detail": (
                        "This request is not linked to a form submission."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CreateAccessLinkSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        expires_in_hours = serializer.validated_data[
            "expires_in_hours"
        ]

        max_edits = serializer.validated_data[
            "max_edits"
        ]

        selected_form = get_object_or_404(
            FormTemplate,
            pk=serializer.validated_data["form_id"],
        )

        raw_editable_fields = serializer.validated_data.get(
            "editable_fields",
            [],
        )

        normalized_editable_fields = []

        sections_queryset = (
            selected_form.sections
            .filter(is_active=True)
            .prefetch_related("fields")
        )

        for section in sections_queryset:
            for field in section.fields.filter(
                    is_active=True
            ):
                if (
                        field.key in raw_editable_fields
                ):
                    normalized_editable_fields.append(
                        field.key
                    )

        link = ServiceRequestAccessLink.objects.create(
            request=advisory_request,
            submission=advisory_request.form_submission,
            form=selected_form,
            created_by=request.user,
            expires_at=(
                    timezone.now()
                    + timedelta(hours=expires_in_hours)
            ),
            max_edits=max_edits,
            editable_fields=normalized_editable_fields,
            snapshot_data=build_submission_snapshot(
                submission=advisory_request.form_submission,
                editable_form=selected_form,
            ),
        )

        AccessActivityService.log(
            request=request,
            link=link,
            action="link_created",
        )

        return Response(
            AccessLinkSerializer(
                link,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )


class AdminRequestAccessLinksView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    def get(self, request, request_id):
        links = (
            ServiceRequestAccessLink.objects
            .filter(
                request_id=request_id,
            )
            .select_related(
                "form",
                "submission",
                "created_by",
            )
            .order_by("-created_at")
        )

        return Response(
            AccessLinkSerializer(
                links,
                many=True,
                context={
                    "request": request,
                },
            ).data
        )


class AdminRevokeAccessLinkView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    def post(self, request, link_id):
        link = get_object_or_404(
            ServiceRequestAccessLink,
            pk=link_id,
        )

        link.status = (
            ServiceRequestAccessLink.STATUS_REVOKED
        )

        link.revoked_at = timezone.now()

        link.save(
            update_fields=[
                "status",
                "revoked_at",
            ]
        )

        AccessActivityService.log(
            request=request,
            link=link,
            action="link_revoked",
        )

        return Response(
            {
                "success": True,
            }
        )


class AdminRegenerateAccessLinkView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    def post(self, request, link_id):
        old_link = get_object_or_404(
            ServiceRequestAccessLink.objects
            .select_related(
                "request",
                "submission",
                "form",
            ),
            pk=link_id,
        )

        if old_link.status == (
                ServiceRequestAccessLink.STATUS_ACTIVE
        ):
            old_link.status = (
                ServiceRequestAccessLink.STATUS_REVOKED
            )
            old_link.revoked_at = timezone.now()
            old_link.save(
                update_fields=[
                    "status",
                    "revoked_at",
                ]
            )

        new_link = ServiceRequestAccessLink.objects.create(
            request=old_link.request,
            submission=old_link.submission,
            form=old_link.form,
            created_by=request.user,
            expires_at=old_link.expires_at,
            editable_fields=old_link.editable_fields,
            max_edits=old_link.max_edits,
            snapshot_data=(
                build_submission_snapshot(
                    submission=old_link.submission,
                    editable_form=old_link.form,
                )
                if old_link.submission
                else {}
            ),
        )

        AccessActivityService.log(
            request=request,
            link=old_link,
            action="link_regenerated_old_revoked",
        )

        AccessActivityService.log(
            request=request,
            link=new_link,
            action="link_regenerated_new_created",
        )

        return Response(
            AccessLinkSerializer(
                new_link,
                context={
                    "request": request,
                },
            ).data,
            status=status.HTTP_201_CREATED,
        )


class AdminEditableSubmissionUpdateView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    def patch(
            self,
            request,
            submission_id,
    ):
        submission = get_object_or_404(
            FormSubmission.objects.select_related(
                "form",
            ),
            pk=submission_id,
        )

        serializer = (
            EditableSubmissionUpdateSerializer(
                data=request.data,
            )
        )

        serializer.is_valid(
            raise_exception=True,
        )

        updated_fields = (
            SubmissionUpdateService
            .update_submission(
                submission=submission,
                cleaned_data=serializer.validated_data[
                    "data"
                ],
                admin_user=request.user,
            )
        )

        # =====================================
        # UPDATE RELATED REQUEST STATUS
        # =====================================

        if hasattr(
                submission,
                "service_request",
        ):
            service_request = (
                submission.service_request
            )

            service_request.status = (
                ServiceAdvisoryRequest
                .STATUS_REVIEWING
            )

            service_request.save(
                update_fields=[
                    "status",
                ]
            )

        AccessActivityService.log(
            request=request,
            link=None,
            action="admin_submission_updated",
            metadata={
                "submission_id": submission.id,
                "updated_fields": updated_fields,
                "admin_id": request.user.id,
            },
        )

        return Response(
            {
                "success": True,
                "updated_fields": updated_fields,
            }
        )


class AdminSubmissionEditHistoryView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    def get(self, request, submission_id):
        submission = get_object_or_404(
            FormSubmission,
            pk=submission_id,
        )

        logs = (
            FormSubmissionEditLog.objects
            .filter(
                submission=submission,
            )
            .select_related(
                "edited_by_admin",
                "edited_by_link",
            )
            .order_by("-edited_at")
        )
        result = []

        for log in logs:
            result.append({
                "id": log.id,
                "field_key": log.field_key,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "created_at": log.edited_at,

                "edited_by_admin": (
                    {
                        "id": log.edited_by_admin.id,
                        "email": log.edited_by_admin.email,
                    }
                    if log.edited_by_admin
                    else None
                ),

                "edited_by_client": (
                    True
                    if log.edited_by_link
                    else False
                ),
            })

        return Response(result)


class AdminAccessActivityLogsView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    def get(self, request, request_id):
        advisory_request = get_object_or_404(
            ServiceAdvisoryRequest,
            pk=request_id,
        )

        logs = (
            ServiceRequestAccessActivity.objects
            .filter(
                link__request=advisory_request,
            )
            .select_related(
                "link",
            )
            .order_by("-created_at")
        )

        result = []

        for log in logs:
            result.append({
                "id": log.id,
                "action": log.action,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "metadata": log.metadata,
                "created_at": log.created_at,

                "link": {
                    "id": log.link.id,
                    "public_key": log.link.public_key,
                }
                if log.link
                else None,
            })

        return Response(result)
