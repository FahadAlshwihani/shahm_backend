from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from form_builder.actions import FORM_ACTIONS
from services.access_security import (
    validate_access_session,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from core.pagination import DefaultPagination
from accounts.permissions import IsEditorOrAbove

from datetime import timedelta

from services.request_otp import (
    ServiceRequestOTP,
)

from services.request_access import (
    ServiceRequestAccessSession,
    ServiceRequestAccessActivity,
)

from .models import (
    FormTemplate,
    FormSection,
    FormField,
    FormFieldOption,
    FormSubmission,
    SuccessResponse,
    InfoModal,
    InfoModalSection,
)

from .serializers import (
    FormTemplateAdminSerializer,
    FormTemplatePublicSerializer,
    FormSectionSerializer,
    FormFieldSerializer,
    FormFieldOptionSerializer,
    FormSubmissionAdminSerializer,
    FormSubmissionStatusSerializer,
    PublicFormSubmitSerializer,
    SuccessResponseSerializer,
    InfoModalSerializer,
    InfoModalSectionSerializer,
    PublicSubmissionUpdateSerializer,
)

from messaging.utils import (
    render_email_template,
)

from messaging.models import (
    EmailTemplate,
)

from email_settings.services import (
    DynamicEmailService,
)

from settings_app.models import (
    SiteSettings,
)

from services.utils.masking import (
    mask_email,
)

from services.models import (
    ServiceRequestAccessLink,
)


class AdminFormTemplateListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        forms = (
            FormTemplate.objects
            .annotate(submissions_count=Count("submissions"))
            .prefetch_related(
                Prefetch(
                    "sections",
                    queryset=FormSection.objects.prefetch_related(
                        Prefetch(
                            "fields",
                            queryset=FormField.objects.prefetch_related("options")
                            .order_by("order", "id"),
                        )
                    ).order_by("order", "id"),
                )
            )
            .order_by("-created_at")
        )

        serializer = FormTemplateAdminSerializer(
            forms,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = FormTemplateAdminSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        form = serializer.save(created_by=request.user)

        return Response(
            FormTemplateAdminSerializer(
                form,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class AdminFormTemplateDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request, pk):
        form = get_object_or_404(
            FormTemplate.objects.prefetch_related(
                "sections__fields__options"
            ),
            pk=pk,
        )
        serializer = FormTemplateAdminSerializer(form, context={"request": request})
        return Response(serializer.data)

    def patch(self, request, pk):
        form = get_object_or_404(FormTemplate, pk=pk)
        serializer = FormTemplateAdminSerializer(
            form,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        form = serializer.save()
        return Response(FormTemplateAdminSerializer(form, context={"request": request}).data)

    def delete(self, request, pk):
        form = get_object_or_404(FormTemplate, pk=pk)

        if form.submissions.exists():
            return Response(
                {"detail": "لا يمكن حذف نموذج عليه ردود. عطّله بدل الحذف."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        form.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminFormSectionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def post(self, request, form_id):
        form = get_object_or_404(FormTemplate, pk=form_id)

        serializer = FormSectionSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        section = serializer.save(form=form)

        return Response(
            FormSectionSerializer(
                section,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class AdminFormSectionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        section = get_object_or_404(
            FormSection.objects.select_related("form"),
            pk=pk,
        )
        serializer = FormSectionSerializer(
            section,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        section = get_object_or_404(FormSection, pk=pk)

        if section.fields.exists():
            section.is_active = False
            section.save(update_fields=["is_active"])

            return Response({
                "detail": "تم تعطيل القسم لأنه يحتوي على حقول."
            })

        section.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminFormFieldListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def post(self, request, form_id):
        form = get_object_or_404(FormTemplate, pk=form_id)

        serializer = FormFieldSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        section = get_object_or_404(
            FormSection,
            pk=request.data.get("section"),
            form=form,
        )

        field = serializer.save(section=section)

        return Response(
            FormFieldSerializer(field, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AdminFormFieldDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        field = get_object_or_404(
            FormField.objects.select_related("section__form"),
            pk=pk,
        )
        serializer = FormFieldSerializer(
            field,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        field = serializer.save()

        return Response(FormFieldSerializer(field, context={"request": request}).data)

    def delete(self, request, pk):
        field = get_object_or_404(FormField, pk=pk)

        if field.submission_values.exists():
            field.is_active = False
            field.save(update_fields=["is_active"])
            return Response({"detail": "تم تعطيل الحقل لأنه مرتبط بردود سابقة."})

        field.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminFormFieldOptionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def post(self, request, field_id):
        field = get_object_or_404(FormField, pk=field_id)

        serializer = FormFieldOptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        option = serializer.save(field=field)

        return Response(
            FormFieldOptionSerializer(option).data,
            status=status.HTTP_201_CREATED,
        )


class AdminFormFieldOptionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        option = get_object_or_404(FormFieldOption, pk=pk)
        serializer = FormFieldOptionSerializer(option, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        option = serializer.save()

        return Response(FormFieldOptionSerializer(option).data)

    def delete(self, request, pk):
        option = get_object_or_404(FormFieldOption, pk=pk)
        option.is_active = False
        option.save(update_fields=["is_active"])
        return Response({"detail": "تم تعطيل الخيار."})


class AdminSuccessResponseListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        responses = (
            SuccessResponse.objects
            .order_by("-created_at")
        )

        serializer = SuccessResponseSerializer(
            responses,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)

    def post(self, request):
        serializer = SuccessResponseSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        response_obj = serializer.save()

        return Response(
            SuccessResponseSerializer(
                response_obj,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class AdminSuccessResponseDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request, pk):
        response_obj = get_object_or_404(
            SuccessResponse,
            pk=pk,
        )

        serializer = SuccessResponseSerializer(
            response_obj,
            context={"request": request},
        )

        return Response(serializer.data)

    def patch(self, request, pk):
        response_obj = get_object_or_404(
            SuccessResponse,
            pk=pk,
        )

        serializer = SuccessResponseSerializer(
            response_obj,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        response_obj = get_object_or_404(
            SuccessResponse,
            pk=pk,
        )

        if response_obj.forms.exists():
            response_obj.is_active = False
            response_obj.save(update_fields=["is_active"])

            return Response({
                "detail": "تم تعطيل Success Response لأنه مرتبط بنماذج."
            })

        response_obj.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminFormSubmissionListView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        form_id = request.GET.get("form")
        status_filter = request.GET.get("status")

        submissions = (
            FormSubmission.objects
            .select_related(
                "form",
                "submitted_by",
            )
            .prefetch_related(
                "values__field",
            )
            .order_by("-submitted_at")
        )

        if form_id:
            submissions = submissions.filter(
                form_id=form_id
            )

        if status_filter:
            submissions = submissions.filter(
                status=status_filter
            )

        paginator = DefaultPagination()

        page = paginator.paginate_queryset(
            submissions,
            request,
        )

        serializer = (
            FormSubmissionAdminSerializer(
                page,
                many=True,
                context={
                    "request": request,
                },
            )
        )

        return paginator.get_paginated_response(
            serializer.data
        )


class AdminFormSubmissionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request, pk):
        submission = get_object_or_404(
            FormSubmission.objects
            .select_related("form", "submitted_by")
            .prefetch_related("values__field"),
            pk=pk,
        )

        serializer = FormSubmissionAdminSerializer(submission, context={"request": request})
        return Response(serializer.data)

    def patch(self, request, pk):
        submission = get_object_or_404(FormSubmission, pk=pk)
        serializer = FormSubmissionStatusSerializer(
            submission,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(FormSubmissionAdminSerializer(submission, context={"request": request}).data)

    def delete(self, request, pk):
        submission = get_object_or_404(FormSubmission, pk=pk)
        submission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicFormListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        forms = (
            FormTemplate.objects
            .filter(is_active=True)
            .prefetch_related(
                "sections__fields__options"
            )
            .order_by("-created_at")
        )

        serializer = FormTemplatePublicSerializer(forms, many=True, context={"request": request})
        return Response(serializer.data)


class PublicFormDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        form = get_object_or_404(
            FormTemplate.objects
            .filter(is_active=True)
            .prefetch_related(
                "sections__fields__options"
            ),
            slug=slug,
        )

        serializer = FormTemplatePublicSerializer(form, context={"request": request})
        return Response(serializer.data)


class PublicFormSubmitView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request, slug):

        form = get_object_or_404(
            FormTemplate.objects
            .select_related("success_response")
            .filter(is_active=True),
            slug=slug,
        )

        if form.requires_login and not request.user.is_authenticated:
            return Response(
                {
                    "detail": "Authentication is required to submit this form."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # =====================================================
        # FORM ACCESS VERIFICATION
        # =====================================================

        if form.requires_verification:

            access_token = request.headers.get(
                "X-Access-Token"
            )

            public_key = request.query_params.get(
                "access_key"
            )

            if not access_token:
                return Response(
                    {
                        "detail": (
                            "Access token required."
                        )
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if not public_key:
                return Response(
                    {
                        "detail": (
                            "Access key required."
                        )
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            validate_access_session(
                public_key=public_key,
                token=access_token,
            )

        if (
                request.user.is_authenticated
                and not form.allow_multiple_submissions
                and FormSubmission.objects.filter(
            form=form,
            submitted_by=request.user
        ).exists()
        ):
            return Response(
                {
                    "detail": "You have already submitted this form."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PublicFormSubmitSerializer(
            data=request.data,
            context={
                "request": request,
                "form": form,
            },
        )

        serializer.is_valid(raise_exception=True)

        submission = serializer.save()

        cleaned_data = {}

        for value in submission.values.all():

            if value.value_json is not None:
                cleaned_data[value.field.key] = value.value_json

            elif value.value_file:
                cleaned_data[value.field.key] = value.value_file

            else:
                cleaned_data[value.field.key] = value.value_text

        action_result = None

        action = FORM_ACTIONS.get(
            form.context_type
        )

        if action:
            try:

                action_result = action.run(
                    form=form,
                    submission=submission,
                    cleaned_data=cleaned_data,
                    files=request.FILES,
                )

            except DjangoValidationError as exc:

                submission.delete()

                return Response(
                    {
                        "success": False,
                        "message": "Validation error",
                        "errors": exc.messages,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        success_payload = None

        if form.success_response and form.success_response.is_active:

            success_payload = SuccessResponseSerializer(
                form.success_response,
                context={"request": request},
            ).data

            if success_payload["show_reference_number"]:

                generated_reference = None

                # =========================================
                # ACTION REFERENCE
                # =========================================
                if (
                        action_result
                        and isinstance(action_result, dict)
                        and action_result.get("reference")
                ):
                    generated_reference = action_result["reference"]

                # =========================================
                # FALLBACK TO FORM SUBMISSION REFERENCE
                # =========================================
                if not generated_reference:
                    generated_reference = submission.public_reference

                success_payload["reference_number"] = (
                    f'{success_payload["reference_prefix"]}'
                    f'{generated_reference}'
                )

        return Response(
            {
                "success": True,
                "submission_reference": submission.public_reference,
                "submission_edit_token": (
                    submission.public_edit_token
                    if form.allow_public_edit
                    else None
                ),
                "success_response": success_payload,
                "action_result": action_result,
            },
            status=status.HTTP_201_CREATED,
        )


class PublicSubmissionUpdateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def patch(self, request, reference):

        submission = get_object_or_404(
            FormSubmission.objects.select_related(
                "form"
            ).prefetch_related(
                "values__field"
            ),
            public_reference=reference,
        )

        form = submission.form

        if not form.allow_public_edit:
            return Response(
                {
                    "detail": "Public editing disabled."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        token = request.headers.get(
            "X-Submission-Token"
        )

        if not token:
            return Response(
                {
                    "detail": "Missing edit token."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if token != submission.public_edit_token:
            return Response(
                {
                    "detail": "Invalid edit token."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if (
                submission.public_edit_expires_at
                and timezone.now() > submission.public_edit_expires_at
        ):
            return Response(
                {
                    "detail": "Edit token expired."
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = PublicSubmissionUpdateSerializer(
            data=request.data,
            context={
                "request": request,
                "form": form,
                "submission": submission,
            },
        )

        serializer.is_valid(raise_exception=True)

        submission = serializer.save()

        return Response({
            "success": True,
            "reference": submission.public_reference,
            "updated_at": submission.updated_at,
        })


class PublicFormSendOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "otp_send"

    OTP_EXPIRY_MINUTES = 5
    RESEND_COOLDOWN_SECONDS = 120

    def post(self, request):
        access_key = request.data.get("access_key")

        if not access_key:
            return Response(
                {"detail": "Access key required."},
                status=400,
            )

        link = get_object_or_404(
            ServiceRequestAccessLink.objects.select_related("request"),
            public_key=access_key,
            status="active",
        )

        request_email = link.request.email

        print(request_email)
        print(mask_email(request_email))

        if not request_email:
            return Response(
                {"detail": "No email attached to request."},
                status=400,
            )

        latest_otp = (
            ServiceRequestOTP.objects
            .filter(link=link)
            .order_by("-created_at")
            .first()
        )



        if latest_otp:
            cooldown_until = (
                    latest_otp.created_at
                    + timedelta(seconds=self.RESEND_COOLDOWN_SECONDS)
            )

            if timezone.now() < cooldown_until:
                remaining = int(
                    (cooldown_until - timezone.now()).total_seconds()
                )

                return Response(
                    {
                        "detail": "Please wait before requesting another code.",
                        "remaining_seconds": remaining,
                    },
                    status=429,
                )

        otp_code = ServiceRequestOTP.generate_code()

        otp = ServiceRequestOTP(
            link=link,
            email=request_email,
            expires_at=(
                    timezone.now()
                    + timedelta(minutes=self.OTP_EXPIRY_MINUTES)
            ),
        )

        otp.set_code(otp_code)
        otp.save()

        ServiceRequestAccessActivity.objects.create(
            link=link,
            action=ServiceRequestAccessActivity.ACTION_OTP_SENT,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        settings = SiteSettings.objects.first()

        subject, html = render_email_template(
            "request_access_otp",
            {
                "name": link.request.first_name or "Client",
                "otp": otp_code,
                "site_name": (
                    settings.site_name_ar
                    if settings
                    else ""
                ),
                "expiry_minutes": str(
                    self.OTP_EXPIRY_MINUTES
                ),
            },
        )

        if subject and html:
            DynamicEmailService.send_email(
                subject=subject,
                body="",
                recipient_list=[request_email],
                html_body=html,
            )

        return Response(
            {
                "success": True,
                "masked_destination": mask_email(request_email),
                "cooldown_seconds": self.RESEND_COOLDOWN_SECONDS,
            }
        )


class PublicFormVerifyOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_scope = "otp_verify"

    MAX_ATTEMPTS = 5
    SESSION_EXPIRY_HOURS = 1

    def post(self, request):
        access_key = request.data.get("access_key")
        otp_code = request.data.get("code")

        if not access_key or not otp_code:
            return Response(
                {
                    "detail": "Access key and OTP required."
                },
                status=400,
            )

        link = get_object_or_404(
            ServiceRequestAccessLink,
            public_key=access_key,
            status="active",
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
            return Response(
                {"detail": "OTP expired."},
                status=400,
            )

        if timezone.now() > otp.expires_at:
            return Response(
                {"detail": "OTP expired."},
                status=400,
            )

        if otp.attempts >= self.MAX_ATTEMPTS:
            return Response(
                {
                    "detail": "Maximum attempts exceeded."
                },
                status=429,
            )

        if not otp.verify_code(otp_code):
            otp.attempts += 1

            otp.save(update_fields=["attempts"])

            ServiceRequestAccessActivity.objects.create(
                link=link,
                action=ServiceRequestAccessActivity.ACTION_OTP_FAILED,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=request.META.get(
                    "HTTP_USER_AGENT",
                    "",
                ),
            )

            return Response(
                {"detail": "Invalid OTP."},
                status=400,
            )

        ServiceRequestOTP.objects.filter(
            link=link,
            is_verified=False,
        ).exclude(
            pk=otp.pk
        ).update(
            expires_at=timezone.now()
        )

        ServiceRequestOTP.objects.filter(
            link=link,
            is_verified=False,
        ).exclude(
            pk=otp.pk
        ).update(
            expires_at=timezone.now()
        )

        otp.is_verified = True

        otp.save(
            update_fields=["is_verified"]
        )

        token = (
            ServiceRequestAccessSession.generate_token()
        )

        session = (
            ServiceRequestAccessSession.objects.create(
                link=link,
                otp=otp,
                token=token,
                expires_at=(
                        timezone.now()
                        + timedelta(
                    hours=self.SESSION_EXPIRY_HOURS
                )
                ),
            )
        )

        ServiceRequestAccessActivity.objects.create(
            link=link,
            action=(
                ServiceRequestAccessActivity.ACTION_OTP_VERIFIED
            ),
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get(
                "HTTP_USER_AGENT",
                "",
            ),
        )

        return Response(
            {
                "success": True,
                "access_token": session.token,
                "expires_in": 3600,
            }
        )


class AdminInfoModalListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        modals = (
            InfoModal.objects
            .prefetch_related("sections")
            .order_by("-id")
        )

        return Response(
            InfoModalSerializer(
                modals,
                many=True,
                context={"request": request},
            ).data
        )

    def post(self, request):
        serializer = InfoModalSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        return Response(
            InfoModalSerializer(
                obj,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class AdminInfoModalDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request, pk):
        obj = get_object_or_404(
            InfoModal.objects.prefetch_related("sections"),
            pk=pk,
        )

        return Response(
            InfoModalSerializer(
                obj,
                context={"request": request},
            ).data
        )

    def patch(self, request, pk):
        obj = get_object_or_404(InfoModal, pk=pk)

        serializer = InfoModalSerializer(
            obj,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        obj = get_object_or_404(InfoModal, pk=pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminInfoModalSectionListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def post(self, request, modal_id):
        modal = get_object_or_404(InfoModal, pk=modal_id)

        serializer = InfoModalSectionSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        section = serializer.save(modal=modal)

        return Response(
            InfoModalSectionSerializer(section).data,
            status=status.HTTP_201_CREATED,
        )


class AdminInfoModalSectionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        section = get_object_or_404(InfoModalSection, pk=pk)

        serializer = InfoModalSectionSerializer(
            section,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):
        section = get_object_or_404(InfoModalSection, pk=pk)
        section.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PublicInfoModalDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        obj = get_object_or_404(
            InfoModal.objects.prefetch_related(
                Prefetch(
                    "sections",
                    queryset=InfoModalSection.objects.filter(
                        is_active=True
                    ).order_by("order")
                )
            ),
            slug=slug,
            is_active=True,
        )

        return Response(
            InfoModalSerializer(
                obj,
                context={"request": request},
            ).data
        )
