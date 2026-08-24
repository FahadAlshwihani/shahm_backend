from django.urls import path
from .views import (
    PublicBlogListView,
    PublicBlogDetailView,
    PublicCategoryListView,
    PublicTagListView,
    PublicBlogSettingsView,
    BlogSettingsUpdateView,

    CategoryListCreateView,
    CategoryDetailView,
    TagListCreateView,
    TagDetailView,
    BlogListCreateView,
    BlogDetailView,
)

urlpatterns = [

    # ==========================
    # PUBLIC ROUTES
    # ==========================

    path("settings/", PublicBlogSettingsView.as_view()),

    path("categories/", PublicCategoryListView.as_view()),
    path("tags/", PublicTagListView.as_view()),

    path("posts/", PublicBlogListView.as_view()),
    path("posts/<slug:slug>/", PublicBlogDetailView.as_view()),

    # ==========================
    # ADMIN ROUTES
    # ==========================

    path("admin/categories/", CategoryListCreateView.as_view()),
    path("admin/categories/<int:pk>/", CategoryDetailView.as_view()),

    path("admin/tags/", TagListCreateView.as_view()),
    path("admin/tags/<int:pk>/", TagDetailView.as_view()),

    path("admin/posts/", BlogListCreateView.as_view()),
    path("admin/posts/<int:pk>/", BlogDetailView.as_view()),

    path("admin/settings/", BlogSettingsUpdateView.as_view()),
]
