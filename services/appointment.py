from rest_framework import serializers
from services.models import AppointmentSlot, AppointmentBooking


class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = [
            "id",
            "date",
            "start_time",
            "end_time",
            "is_available",
        ]

class AppointmentBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentBooking
        fields = [
            "id",
            "slot",
            "first_name",
            "last_name",
            "email",
            "phone",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]
