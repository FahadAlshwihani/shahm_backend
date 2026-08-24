# settings_app/urls.py
from django.urls import path
from .views import (
    SiteSettingsView,
    EmailSettingsView,
    EmailSMTPTestView,
)

urlpatterns = [
    path("", SiteSettingsView.as_view(), name="site-settings"),

    # SMTP settings
    path("email/", EmailSettingsView.as_view(), name="email-settings"),

    # Test SMTP
    path("email/test/", EmailSMTPTestView.as_view(), name="email-test"),

]
