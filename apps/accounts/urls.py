# accounts/urls.py

from django.conf import settings
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    FirstAdminSetupView,
    LoginView,
    UsersListView,
    CreateUserView,
    UserDetailView,
)

urlpatterns = [
    # =========================================================
    # AUTHENTICATION
    # =========================================================
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # =========================================================
    # USER ADMINISTRATION
    # =========================================================
    path("users/", UsersListView.as_view(), name="users-list"),
    path("users/create/", CreateUserView.as_view(), name="user-create"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]

if settings.ENABLE_INITIAL_ADMIN_SETUP:
    urlpatterns.insert(
        0,
        path("super/init/", FirstAdminSetupView.as_view(), name="super-init"),
    )
