from django.urls import path
from .views import (
    PublicSEOView,
    DefaultSEOView,
    PageSEOListCreateView,
    PageSEODetailView,
    AllPagesForSEO,
)

urlpatterns = [
    # PUBLIC SEO
    path("public/", PublicSEOView.as_view()),             # ← default SEO
    path("public/<slug:slug>/", PublicSEOView.as_view()), # ← page SEO

    # ADMIN DEFAULT SEO
    path("admin/default/", DefaultSEOView.as_view()),

    # ADMIN PAGE SEO CRUD
    path("admin/pages/", PageSEOListCreateView.as_view()),
    path("admin/pages/<int:pk>/", PageSEODetailView.as_view()),

    # ADMIN ALL PAGES LIST
    path("admin/all-pages/", AllPagesForSEO.as_view()),
]
