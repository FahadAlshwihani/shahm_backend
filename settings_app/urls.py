# settings_app/urls.py
from django.urls import path
from .views import (
    SiteSettingsView,
    EmailSettingsView,
    EmailTemplateView,
    EmailSMTPTestView,
)

urlpatterns = [
    path("", SiteSettingsView.as_view(), name="site-settings"),

    # SMTP settings
    path("email/", EmailSettingsView.as_view(), name="email-settings"),

    # Test SMTP
    path("email/test/", EmailSMTPTestView.as_view(), name="email-test"),

    # HTML templates
    path("email-templates/", EmailTemplateView.as_view(), name="email-template"),
]
