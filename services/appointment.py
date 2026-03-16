from rest_framework import serializers
from django.utils import timezone

from services.models import AppointmentSlot, AppointmentBooking



class AppointmentSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = [
            "id",
            "date",
            "start_time",
            "end_time",
            "shift",
            "is_available",
        ]

    def validate(self, data):
        date = data.get("date", getattr(self.instance, "date", None))
        start = data.get("start_time", getattr(self.instance, "start_time", None))
        end = data.get("end_time", getattr(self.instance, "end_time", None))
        shift = data.get("shift", getattr(self.instance, "shift", None))

        if not date or not start or not end or not shift:
            raise serializers.ValidationError(
                "Date, start time, end time, and shift are required"
            )

        if shift not in ["morning", "evening"]:
            raise serializers.ValidationError("Invalid shift")

        if date < timezone.localdate():
            raise serializers.ValidationError("Cannot create slot in the past")

        now_local = timezone.localtime()
        if date == now_local.date() and start <= now_local.time():
            raise serializers.ValidationError("Cannot create slot in the past")

        if start >= end:
            raise serializers.ValidationError("End time must be after start time")

        qs = AppointmentSlot.objects.filter(
            date=date,
            start_time=start,
        )

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Slot already exists")

        return data


class AppointmentBookingSerializer(serializers.ModelSerializer):

    slot_date = serializers.DateField(source="slot.date", read_only=True)
    slot_start = serializers.TimeField(source="slot.start_time", read_only=True)
    slot_end = serializers.TimeField(source="slot.end_time", read_only=True)
    slot_shift = serializers.CharField(source="slot.shift", read_only=True)

    attachment = serializers.SerializerMethodField()
    voice_note = serializers.SerializerMethodField()

    def get_attachment(self, obj):
        request = self.context.get("request")
        if obj.attachment:
            if request:
                return request.build_absolute_uri(obj.attachment.url)
            return obj.attachment.url
        return None

    def get_voice_note(self, obj):
        request = self.context.get("request")
        if obj.voice_note:
            if request:
                return request.build_absolute_uri(obj.voice_note.url)
            return obj.voice_note.url
        return None


    class Meta:
        model = AppointmentBooking
        fields = [
            "id",
            "slot",
            "slot_date",
            "slot_start",
            "slot_end",
            "slot_shift",
            "appointment_type",
            "title",
            "first_name",
            "last_name",
            "email",
            "phone",
            "visitors",
            "message",
            "attachment",
            "voice_note",
            "status",
            "reference",
            "created_at",
        ]
        read_only_fields = [
            "reference",
            "created_at",
        ]