# accounts/urls.py

from django.urls import path
from .views import (
    FirstAdminSetupView,
    LoginView,
    UsersListView,
    CreateUserView,
    UserDetailView,   # ← هذا هو الصحيح الآن
)

urlpatterns = [
    path("super/init/", FirstAdminSetupView.as_view(), name="super-init"),
    path("login/", LoginView.as_view(), name="login"),

    # List users
    path("users/", UsersListView.as_view(), name="users-list"),

    # Create user
    path("users/create/", CreateUserView.as_view(), name="user-create"),

    # GET (optional) + PATCH + DELETE
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
