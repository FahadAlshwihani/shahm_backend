from django.urls import path
from .views import EmailSettingsView

urlpatterns = [
    path("", EmailSettingsView.as_view(), name="email-settings"),
]
