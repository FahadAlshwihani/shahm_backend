from rest_framework import viewsets
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from django.db.models import Count
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
)
from rest_framework.filters import SearchFilter

from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsEditorOrAbove
from rest_framework.views import APIView
from rest_framework.response import Response

from .imports.service_excel import ServiceExcelImporter

from .models import (
    MainService,
    Service,
    ServiceSection,
    ServicePageCMS,
    ServiceAdvisoryPage,
    ServiceAdvisoryRequest,
    CareerJob,
    CareerApplication,
)

from .serializers import (
    MainServiceSerializer,
    ServiceSerializer,
    ServiceSectionSerializer,
    ServicePageCMSSerializer,
    ServiceAdvisoryPageSerializer,
    ServiceAdvisoryRequestSerializer,
    CareerJobSerializer,
    CareerApplicationSerializer,
)


# =========================================================
# PUBLIC SERVICES
# =========================================================

class PublicMainServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        MainService.objects
        .filter(is_active=True)
        .order_by("order")
    )

    serializer_class = MainServiceSerializer

    permission_classes = [AllowAny]

    lookup_field = "slug"


class PublicServiceViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        queryset = (
            Service.objects
            .filter(is_active=True)
            .select_related("main_service")
            .prefetch_related("sections")
            .order_by("order", "id")
        )

        main_service_id = (
                self.request.query_params.get("main_service")
                or self.request.query_params.get("category")
        )

        if main_service_id:
            queryset = queryset.filter(
                main_service_id=main_service_id
            )

        return queryset

    serializer_class = ServiceSerializer

    permission_classes = [AllowAny]

    lookup_field = "slug"

    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
    ]

    search_fields = [
        "title_ar",
        "title_en",
        "serial_number",
        "short_description_ar",
        "short_description_en",
    ]

    filterset_fields = [
        "main_service",
        "is_featured",
    ]


class PublicServicePageCMSViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServicePageCMS.objects.filter(
        is_active=True
    )

    serializer_class = ServicePageCMSSerializer

    permission_classes = [AllowAny]


# =========================================================
# ADMIN SERVICES
# =========================================================

class AdminMainServiceViewSet(viewsets.ModelViewSet):
    queryset = MainService.objects.all()

    serializer_class = MainServiceSerializer

    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]


class AdminServiceViewSet(viewsets.ModelViewSet):
    queryset = (
        Service.objects
        .select_related("main_service")
        .prefetch_related("sections")
        .all()
    )

    serializer_class = ServiceSerializer

    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
    ]

    search_fields = [
        "title_ar",
        "title_en",
        "serial_number",
    ]

    filterset_fields = [
        "main_service",
        "is_active",
    ]


class AdminServiceSectionViewSet(viewsets.ModelViewSet):
    queryset = ServiceSection.objects.all()

    serializer_class = ServiceSectionSerializer

    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]


class AdminServicePageCMSViewSet(viewsets.ModelViewSet):
    queryset = ServicePageCMS.objects.all()

    serializer_class = ServicePageCMSSerializer

    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]


class AdminServiceAdvisoryPageViewSet(viewsets.ModelViewSet):
    queryset = ServiceAdvisoryPage.objects.all()

    serializer_class = ServiceAdvisoryPageSerializer

    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]


class AdminServiceAdvisoryRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceAdvisoryRequestSerializer

    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
    ]

    search_fields = [
        "reference",
        "email",
        "phone",
        "first_name",
        "last_name",
    ]

    filterset_fields = [
        "status",
    ]

    def get_queryset(self):
        return (
            ServiceAdvisoryRequest.objects
            .select_related(
                "form_submission",
                "form_submission__form",
            )
            .prefetch_related(
                "items__service",
                "access_links",
            )
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            self.get_queryset()
        )

        # ─────────────────────────────
        # Status statistics
        # ─────────────────────────────
        status_counts_qs = (
            queryset
            .values("status")
            .annotate(count=Count("id"))
        )

        status_counts = {
            item["status"]: item["count"]
            for item in status_counts_qs
        }

        # ─────────────────────────────
        # Default DRF pagination
        # ─────────────────────────────
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )

            paginated_response = (
                self.get_paginated_response(
                    serializer.data
                )
            )

            # inject custom stats
            paginated_response.data[
                "status_counts"
            ] = status_counts

            return paginated_response

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response({
            "count": queryset.count(),
            "status_counts": status_counts,
            "results": serializer.data,
        })


# =========================================================
# CAREERS
# =========================================================

class PublicCareerJobsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        CareerJob.objects
        .filter(is_active=True)
        .order_by("order")
    )

    serializer_class = CareerJobSerializer

    permission_classes = [AllowAny]


class AdminCareerJobsViewSet(viewsets.ModelViewSet):
    queryset = CareerJob.objects.all()

    serializer_class = CareerJobSerializer

    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]


class AdminCareerApplicationsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CareerApplicationSerializer
    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    def get_queryset(self):
        return (
            CareerApplication.objects
            .select_related(
                "job",
                "form_submission",
                "form_submission__form",
            )
            .prefetch_related(
                "form_submission__values__field",
            )
            .order_by("-created_at")
        )


class AdminImportServicesView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsEditorOrAbove,
    ]

    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response(
                {"detail": "Excel file required"},
                status=400
            )

        importer = ServiceExcelImporter(file)

        result = importer.execute()

        return Response(result)


class PublicServicesByMainServiceView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        main_service_id = request.GET.get("main_service")

        services = Service.objects.filter(
            is_active=True
        )

        if main_service_id:
            services = services.filter(
                main_service_id=main_service_id
            )

        services = services.order_by("order", "id")

        return Response([
            {
                "id": service.id,
                "title_ar": service.title_ar,
                "title_en": service.title_en,
                "slug": service.slug,
            }
            for service in services
        ])
