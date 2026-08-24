from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    PublicMainServiceViewSet,
    PublicServiceViewSet,
    PublicServicePageCMSViewSet,

    AdminMainServiceViewSet,
    AdminServiceViewSet,
    AdminServiceSectionViewSet,
    AdminServicePageCMSViewSet,
    AdminServiceAdvisoryPageViewSet,
    AdminServiceAdvisoryRequestViewSet,

    PublicCareerJobsViewSet,
    AdminCareerJobsViewSet,
    AdminCareerApplicationsViewSet,

    AdminImportServicesView, PublicServicesByMainServiceView,
)

from .access.views import (
    SendOTPView,
    VerifyOTPView,
    EditableSubmissionSnapshotView,
    EditableSubmissionUpdateView,
    AdminCreateAccessLinkView,
    AdminRequestAccessLinksView,
    AdminRevokeAccessLinkView,
    AdminRegenerateAccessLinkView,
    AdminEditableSubmissionUpdateView, AdminAccessActivityLogsView, AdminSubmissionEditHistoryView
)

# =========================
# APPOINTMENTS
# =========================

from apps.services.appointments.admin_views import (
    AdminAppointmentPageView,
    AdminAppointmentSettingsView,
    AdminAppointmentSlotsView,
    AdminAppointmentSlotDetailView,
    AdminAppointmentBookingsView,
    AdminGenerateSlotsView,
    AdminCancelBookingView,
    AdminUpdateBookingStatusView,
)

from apps.services.appointments.public_views import (
    PublicAppointmentPageView,
    PublicAppointmentSettingsView,
    PublicAvailableSlotsView,
)

from apps.services.clients.views import (
    AdminClientsView,
    AdminClientFilesView,
)

router = DefaultRouter()

# =========================================================
# PUBLIC SERVICES
# =========================================================

router.register(
    r"public/main-services",
    PublicMainServiceViewSet,
    basename="public-main-services",
)

router.register(
    r"public/services",
    PublicServiceViewSet,
    basename="public-services",
)

router.register(
    r"public/services-page",
    PublicServicePageCMSViewSet,
    basename="public-services-page",
)

# =========================================================
# ADMIN SERVICES
# =========================================================

router.register(
    r"admin/main-services",
    AdminMainServiceViewSet,
    basename="admin-main-services",
)

router.register(
    r"admin/services",
    AdminServiceViewSet,
    basename="admin-services",
)

router.register(
    r"admin/service-sections",
    AdminServiceSectionViewSet,
    basename="admin-service-sections",
)

router.register(
    r"admin/services-page",
    AdminServicePageCMSViewSet,
    basename="admin-services-page",
)

router.register(
    r"admin/service-advisory-page",
    AdminServiceAdvisoryPageViewSet,
    basename="admin-service-advisory-page",
)

router.register(
    r"admin/service-advisory-requests",
    AdminServiceAdvisoryRequestViewSet,
    basename="admin-service-advisory-requests",
)

# =========================================================
# CAREERS
# =========================================================

router.register(
    r"public/careers/jobs",
    PublicCareerJobsViewSet,
    basename="public-careers-jobs",
)

router.register(
    r"admin/careers/jobs",
    AdminCareerJobsViewSet,
    basename="admin-careers-jobs",
)

router.register(
    r"admin/careers/applications",
    AdminCareerApplicationsViewSet,
    basename="admin-careers-applications",
)

urlpatterns = [

    path("", include(router.urls)),

    # =====================================================
    # APPOINTMENTS PUBLIC
    # =====================================================

    path(
        "public/appointments/page/",
        PublicAppointmentPageView.as_view()
    ),

    path(
        "public/appointments/settings/",
        PublicAppointmentSettingsView.as_view()
    ),

    path(
        "public/appointments/slots/",
        PublicAvailableSlotsView.as_view()
    ),

    # =====================================================
    # APPOINTMENTS ADMIN
    # =====================================================

    path(
        "admin/appointments/page/",
        AdminAppointmentPageView.as_view()
    ),

    path(
        "admin/appointments/settings/",
        AdminAppointmentSettingsView.as_view()
    ),

    path(
        "admin/appointments/slots/",
        AdminAppointmentSlotsView.as_view()
    ),

    path(
        "admin/appointments/slots/<int:pk>/",
        AdminAppointmentSlotDetailView.as_view()
    ),

    path(
        "admin/appointments/bookings/",
        AdminAppointmentBookingsView.as_view()
    ),

    path(
        "admin/appointments/slots/generate/",
        AdminGenerateSlotsView.as_view()
    ),

    path(
        "admin/appointments/bookings/<int:pk>/cancel/",
        AdminCancelBookingView.as_view()
    ),

    path(
        "admin/appointments/bookings/<int:pk>/status/",
        AdminUpdateBookingStatusView.as_view()
    ),

    # =====================================================
    # CLIENTS
    # =====================================================

    path(
        "admin/clients/",
        AdminClientsView.as_view()
    ),

    path(
        "admin/clients/<int:pk>/files/",
        AdminClientFilesView.as_view()
    ),

    # =====================================================
    # Excel Import
    # =====================================================

    path(
        "admin/import-services/",
        AdminImportServicesView.as_view()
    ),

    # =====================================================
    # Access OTP
    # =====================================================

    path(
        "public/request-access/send-otp/",
        SendOTPView.as_view()
    ),

    path(
        "public/request-access/verify-otp/",
        VerifyOTPView.as_view()
    ),

    path(
        "public/request-access/<str:public_key>/",
        EditableSubmissionSnapshotView.as_view()
    ),

    path(
        "public/request-access/<str:public_key>/update/",
        EditableSubmissionUpdateView.as_view()
    ),
    path(
        "admin/service-advisory-requests/<int:request_id>/access-links/",
        AdminRequestAccessLinksView.as_view(),
    ),
    path(
        "admin/service-advisory-requests/<int:request_id>/access-links/create/",
        AdminCreateAccessLinkView.as_view(),
    ),
    path(
        "admin/request-access-links/<int:link_id>/revoke/",
        AdminRevokeAccessLinkView.as_view(),
    ),
    path(
        "admin/request-access-links/<int:link_id>/regenerate/",
        AdminRegenerateAccessLinkView.as_view(),
    ),

    path(
        "admin/submissions/<int:submission_id>/update/",
        AdminEditableSubmissionUpdateView.as_view(),
    ),

    path(
        "admin/submissions/<int:submission_id>/history/",
        AdminSubmissionEditHistoryView.as_view(),
    ),

    path(
        "admin/service-advisory-requests/<int:request_id>/logs/",
        AdminAccessActivityLogsView.as_view(),
    ),

    path(
        "services/filter/",
        PublicServicesByMainServiceView.as_view(),
    ),
]
