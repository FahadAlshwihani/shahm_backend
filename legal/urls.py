from django.urls import path
from .views import (
    PublicLegalPageView,
    LegalPageListCreateView,
    LegalPageDetailView,
)

urlpatterns = [
    # Public
    path("<slug:slug>/", PublicLegalPageView.as_view()),

    # Admin (Dashboard)
    path("admin/pages/", LegalPageListCreateView.as_view()),
    path("admin/pages/<int:pk>/", LegalPageDetailView.as_view()),
]
