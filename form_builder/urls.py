from django.urls import path

from .views import (
    AdminFormTemplateListCreateView,
    AdminFormTemplateDetailView,
    AdminFormFieldListCreateView,
    AdminFormFieldDetailView,
    AdminFormFieldOptionListCreateView,
    AdminFormFieldOptionDetailView,
    AdminFormSubmissionListView,
    AdminFormSubmissionDetailView,
    PublicFormListView,
    PublicFormDetailView,
    PublicFormSubmitView,
    AdminFormSectionListCreateView,
    AdminFormSectionDetailView,
    AdminSuccessResponseListCreateView,
    AdminSuccessResponseDetailView,
    PublicFormSendOTPView,
    PublicFormVerifyOTPView,
    AdminInfoModalListCreateView,
    AdminInfoModalDetailView,
    AdminInfoModalSectionListCreateView,
    AdminInfoModalSectionDetailView,
    PublicInfoModalDetailView,
    PublicSubmissionUpdateView,
)

urlpatterns = [

    # =========================
    # Public
    # =========================

    path("public/forms/", PublicFormListView.as_view()),
    path("public/forms/<slug:slug>/", PublicFormDetailView.as_view()),
    path("public/forms/<slug:slug>/submit/", PublicFormSubmitView.as_view()),
    path(
        "public/submissions/<str:reference>/edit/",
        PublicSubmissionUpdateView.as_view(),
    ),

    # =========================
    # Admin - Forms
    # =========================

    path("admin/forms/", AdminFormTemplateListCreateView.as_view()),
    path("admin/forms/<int:pk>/", AdminFormTemplateDetailView.as_view()),

    # =========================
    # Admin - Sections
    # =========================

    path(
        "admin/forms/<int:form_id>/sections/",
        AdminFormSectionListCreateView.as_view(),
    ),

    path(
        "admin/forms/sections/<int:pk>/",
        AdminFormSectionDetailView.as_view(),
    ),

    # =========================
    # Admin - Fields
    # =========================

    path(
        "admin/forms/<int:form_id>/fields/",
        AdminFormFieldListCreateView.as_view(),
    ),

    path(
        "admin/forms/fields/<int:pk>/",
        AdminFormFieldDetailView.as_view(),
    ),

    # =========================
    # Admin - Options
    # =========================

    path(
        "admin/forms/fields/<int:field_id>/options/",
        AdminFormFieldOptionListCreateView.as_view(),
    ),

    path(
        "admin/forms/options/<int:pk>/",
        AdminFormFieldOptionDetailView.as_view(),
    ),

    # =========================
    # Admin - Success Responses
    # =========================

    path(
        "admin/success-responses/",
        AdminSuccessResponseListCreateView.as_view(),
    ),

    path(
        "admin/success-responses/<int:pk>/",
        AdminSuccessResponseDetailView.as_view(),
    ),

    # =========================
    # Admin - Submissions
    # =========================

    path(
        "admin/form-submissions/",
        AdminFormSubmissionListView.as_view(),
    ),

    path(
        "admin/form-submissions/<int:pk>/",
        AdminFormSubmissionDetailView.as_view(),
    ),

    # =========================
    # Public - OTP
    # =========================

    path(
        "public/forms/access/send-otp/",
        PublicFormSendOTPView.as_view(),
    ),

    path(
        "public/forms/access/verify-otp/",
        PublicFormVerifyOTPView.as_view(),
    ),

    # =========================
    # Public - Info Modals
    # =========================
    path(
        "public/info-modals/<slug:slug>/",
        PublicInfoModalDetailView.as_view(),
    ),

    # =========================
    # Admin - Info Modals
    # =========================
    path(
        "admin/info-modals/",
        AdminInfoModalListCreateView.as_view(),
    ),
    path(
        "admin/info-modals/<int:pk>/",
        AdminInfoModalDetailView.as_view(),
    ),
    path(
        "admin/info-modals/<int:modal_id>/sections/",
        AdminInfoModalSectionListCreateView.as_view(),
    ),
    path(
        "admin/info-modal-sections/<int:pk>/",
        AdminInfoModalSectionDetailView.as_view(),
    ),
]
