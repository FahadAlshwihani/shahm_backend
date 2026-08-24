from django.urls import path

from .views_public import (
    PublicSiteSettingsView,
    PublicHeaderView,

    PublicHeroView,
    PublicFooterView,

    PublicPageView,
    PublicLegalPageView,

    PublicBlogListView,
    PublicBlogDetailView,

    PublicTeamView,

    PublicSEOView,

    DashboardStatsView,
)

from apps.cms.views import PublicHomeView


urlpatterns = [
    # Settings
    path("settings/", PublicSiteSettingsView.as_view()),
    path("header/", PublicHeaderView.as_view()),

    # Dashboard
    path("admin/dashboard-stats/", DashboardStatsView.as_view()),

    # Hero / Home / Footer
    path("hero/<slug:slug>/", PublicHeroView.as_view()),
    path("footer/", PublicFooterView.as_view()),
    path("home/", PublicHomeView.as_view()),

    # CMS Pages
    path("page/<slug:slug>/", PublicPageView.as_view()),

    # Legal Pages
    path("legal/<slug:slug>/", PublicLegalPageView.as_view()),



    # Blog (Public)
    path("blog/", PublicBlogListView.as_view()),
    path("blog/<slug:slug>/", PublicBlogDetailView.as_view()),

    # Team
    path("team/", PublicTeamView.as_view()),

    # SEO
    path("seo/", PublicSEOView.as_view()),
    path("seo/<slug:slug>/", PublicSEOView.as_view()),
]
