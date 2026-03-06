from rest_framework import serializers
from services.models import AppointmentPage, AppointmentSettings


class AppointmentPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentPage
        fields = "__all__"


class AppointmentSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSettings
        fields = "__all__"
