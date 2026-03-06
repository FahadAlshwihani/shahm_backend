from django.urls import path
from .views import (
    # Public
    PublicHeroView,
    PublicPageView,
    PublicHomeView,
    PublicHeaderView,
    public_search,
    PublicContactPageView,

    # Admin - Hero
    HeroListCreateView,
    HeroDetailView,

    # Admin - Hero Media
    HeroMediaListCreateView,
    HeroMediaDetailView,

    # Admin - Pages
    PageListCreateView,
    PageDetailView,

    # Admin - Home Sections
    HomeSectionListCreateView,
    HomeSectionDetailView,

    # Admin - Header
    HeaderLinkListCreateView,
    HeaderLinkDetailView,

    # Admin - Footer
    FooterColumnListCreateView,
    FooterColumnDetailView,
    FooterLinkListCreateView,
    FooterLinkDetailView,

    # FAQ
    PublicFAQView,
    FAQListCreateView,
    FAQDetailView,

    # ---------- Contact Admin ----------
    ContactCardListCreateView,
    ContactCardDetailView,

    ContactFAQPreviewView,
    ContactFAQPreviewToggleView,
    ContactPageSettingsAdminView,

    PublicPageContentView,
    AdminPageContentView,
)

urlpatterns = [

    # ------------------- Public -------------------
    path("public/hero/<slug:slug>/", PublicHeroView.as_view()),
    path("public/page/<slug:slug>/", PublicPageView.as_view()),
    path("public/home/", PublicHomeView.as_view()),
    path("public/header/", PublicHeaderView.as_view()),
    path("public/search/", public_search),


    # ------------------- Hero -------------------
    path("admin/heroes/", HeroListCreateView.as_view()),
    path("admin/heroes/<int:pk>/", HeroDetailView.as_view()),

    # --- Hero Media ---
    path("admin/hero-media/<int:hero_id>/", HeroMediaListCreateView.as_view()),
    path("admin/hero-media/item/<int:pk>/", HeroMediaDetailView.as_view()),

    # ------------------- Pages -------------------
    path("admin/pages/", PageListCreateView.as_view()),
    path("admin/pages/<int:pk>/", PageDetailView.as_view()),

    # ------------------- Home Sections -------------------
    path("admin/home-sections/", HomeSectionListCreateView.as_view()),
    path("admin/home-sections/<int:pk>/", HomeSectionDetailView.as_view()),

    # ------------------- Header -------------------
    path("admin/header/", HeaderLinkListCreateView.as_view()),
    path("admin/header/<int:pk>/", HeaderLinkDetailView.as_view()),

    # ------------------- Footer -------------------
    path("admin/columns/", FooterColumnListCreateView.as_view()),
    path("admin/columns/<int:pk>/", FooterColumnDetailView.as_view()),

    path("admin/footer-links/", FooterLinkListCreateView.as_view()),
    path("admin/footer-links/<int:pk>/", FooterLinkDetailView.as_view()),

    # ------------------- FAQ -------------------
    path("public/faq/", PublicFAQView.as_view()),

    path("admin/faq/", FAQListCreateView.as_view()),
    path("admin/faq/<int:pk>/", FAQDetailView.as_view()),

    # Contact Page
    path("public/contact-page/", PublicContactPageView.as_view()),


    # Contact Page Header
    path("admin/contact/page/", ContactPageSettingsAdminView.as_view()),


    path("admin/contact/faq-preview/", ContactFAQPreviewView.as_view()),
    path("admin/contact/faq-preview/toggle/", ContactFAQPreviewToggleView.as_view()),

    path("admin/contact/cards/", ContactCardListCreateView.as_view()),
    path("admin/contact/cards/<int:pk>/", ContactCardDetailView.as_view()),

    path("public/<slug:slug>/", PublicPageContentView.as_view()),
    path("admin/<slug:slug>/", AdminPageContentView.as_view()),


]
