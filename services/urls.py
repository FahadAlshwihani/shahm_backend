from django.urls import path

from services.appointment_admin import (
    AdminAppointmentPageView,
    AdminAppointmentSettingsView,
    AdminAppointmentSlotsView,
    AdminAppointmentSlotDetailView,
    AdminAppointmentBookingsView,
    AdminGenerateSlotsView,
    AdminCancelBookingView,
    AdminUpdateBookingStatusView,
)

from services.client_views import AdminClientsView, AdminClientFilesView

from services.appointment_public import (
    PublicAppointmentPageView,
    PublicAppointmentSettingsView,
    PublicAvailableSlotsView,
    BookAppointmentView,
)


from .views import (
    PublicPracticeAreasView,
    PublicPracticeAreaDetailView,
    PracticeAreaListCreateView,
    PracticeAreaDetailView,
    ServiceListCreateView,
    ServiceDetailView,
    PublicServiceAdvisoryPageView,
    AdminServiceAdvisoryPageView,
    SubmitServiceAdvisoryRequest,
    AdminServiceAdvisoryRequestsView,
    AdminServiceAdvisoryRequestDetailView,
    PublicServicesListView,
    AdminServiceAdvisoryDownloadView,

    # ===== CAREERS =====
    PublicCareerJobsView,
    SubmitCareerApplication,
    AdminCareerJobsView,
    AdminCareerJobDetailView,
    AdminCareerApplicationsView,
    PublicServiceDetailView,
)


urlpatterns = [

    # ===================== PUBLIC (Specific first) =====================

    path(
        "public/service-advisory/",
        PublicServiceAdvisoryPageView.as_view(),
        name="public-service-advisory"
    ),

    path(
        "public/service-advisory/submit/",
        SubmitServiceAdvisoryRequest.as_view(),
        name="submit-service-advisory"
    ),

    # ===================== PUBLIC (General) =====================

    path(
        "public/",
        PublicPracticeAreasView.as_view(),
        name="public-areas"
    ),

path(
    "public/services/",
    PublicServicesListView.as_view(),
    name="public-services"
),

path(
    "public/service/<slug:slug>/",
    PublicServiceDetailView.as_view(),
    name="public-service-detail"
),



    path(
        "public/<slug:slug>/",
        PublicPracticeAreaDetailView.as_view(),
        name="public-area-detail"
    ),

    # ===================== ADMIN =====================

    path(
        "admin/areas/",
        PracticeAreaListCreateView.as_view()
    ),

    path(
        "admin/areas/<int:pk>/",
        PracticeAreaDetailView.as_view()
    ),

    path(
        "admin/items/",
        ServiceListCreateView.as_view()
    ),

    path(
        "admin/items/<int:pk>/",
        ServiceDetailView.as_view()
    ),

    path(
        "admin/service-advisory/",
        AdminServiceAdvisoryPageView.as_view()
    ),

    path(
        "admin/service-advisory/requests/",
        AdminServiceAdvisoryRequestsView.as_view()
    ),

    path(
        "admin/service-advisory/requests/<int:pk>/",
        AdminServiceAdvisoryRequestDetailView.as_view()
    ),

path(
    "admin/service-advisory/requests/<int:pk>/download/",
    AdminServiceAdvisoryDownloadView.as_view(),
    name="service-advisory-download"
),

# ===================== APPOINTMENTS =====================

# PUBLIC
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

# ADMIN
path(
    "admin/appointments/page/",
    AdminAppointmentPageView.as_view()
),
path(
    "admin/appointments/settings/",
    AdminAppointmentSettingsView.as_view()
),

path(
    "public/appointments/book/",
    BookAppointmentView.as_view()
),


# ADMIN
path("admin/appointments/slots/", AdminAppointmentSlotsView.as_view()),
path("admin/appointments/slots/<int:pk>/", AdminAppointmentSlotDetailView.as_view()),
path("admin/appointments/bookings/", AdminAppointmentBookingsView.as_view()),
path("admin/appointments/slots/generate/", AdminGenerateSlotsView.as_view()),
path("admin/appointments/bookings/<int:pk>/cancel/", AdminCancelBookingView.as_view()),
path(
    "admin/appointments/bookings/<int:pk>/status/",
    AdminUpdateBookingStatusView.as_view()
),


     path("admin/clients/", AdminClientsView.as_view()),
     path("admin/clients/<int:pk>/files/", AdminClientFilesView.as_view()),

# ===================== CAREERS =====================

path("public/careers/jobs/", PublicCareerJobsView.as_view()),
path("public/careers/apply/", SubmitCareerApplication.as_view()),

path("admin/careers/jobs/", AdminCareerJobsView.as_view()),
path("admin/careers/jobs/<int:pk>/", AdminCareerJobDetailView.as_view()),
path("admin/careers/applications/", AdminCareerApplicationsView.as_view()),




]
