from rest_framework import serializers
from django.utils import timezone

from apps.services.models import AppointmentSlot, AppointmentBooking



class AppointmentSlotSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(
        format="%H:%M"
    )

    end_time = serializers.TimeField(
        format="%H:%M"
    )

    slot_label = serializers.SerializerMethodField()
    class Meta:
        model = AppointmentSlot
        fields = [
            "id",
            "date",
            "start_time",
            "end_time",
            "shift",
            "is_available",
            "slot_label",
        ]

    def validate(self, data):
        date = data.get("date", getattr(self.instance, "date", None))
        start = data.get("start_time", getattr(self.instance, "start_time", None))
        end = data.get("end_time", getattr(self.instance, "end_time", None))
        if not date or not start or not end:
            raise serializers.ValidationError(
                "Date, start time, end time, and shift are required"
            )

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

        data["shift"] = (
            "morning"
            if start.hour < 12
            else "evening"
        )

        return data

    def get_slot_label(self, obj):
        return (
            f"{obj.date} | "
            f"{obj.start_time.strftime('%H:%M')} - "
            f"{obj.end_time.strftime('%H:%M')}"
        )


class AppointmentBookingSerializer(serializers.ModelSerializer):
    slot_date = serializers.DateField(
        source="slot_date_snapshot",
        read_only=True,
    )

    slot_start = serializers.TimeField(
        source="slot_start_snapshot",
        read_only=True,
    )

    slot_end = serializers.TimeField(
        source="slot_end_snapshot",
        read_only=True,
    )

    slot_shift = serializers.CharField(
        source="slot_shift_snapshot",
        read_only=True,
    )

    slot_label = serializers.CharField(
        source="slot_label_snapshot",
        read_only=True,
    )

    dynamic_fields = serializers.SerializerMethodField()


    class Meta:
        model = AppointmentBooking
        fields = [
            "id",
            "slot",
            "slot_date",
            "slot_start",
            "slot_end",
            "slot_shift",
            "slot_label",
            "status",
            "reference",
            "created_at",
            "dynamic_fields",
        ]
        read_only_fields = [
            "reference",
            "created_at",
        ]

    def get_dynamic_fields(self, obj):
        if not obj.form_submission:
            return []

        values = (
            obj.form_submission.values
            .select_related("field")
            .all()
        )

        result = []

        for value in values:
            field = value.field

            request = self.context.get("request")

            if value.value_json is not None:
                field_value = value.value_json

            elif value.value_file:
                if request:
                    field_value = request.build_absolute_uri(
                        value.value_file.url
                    )
                else:
                    field_value = value.value_file.url

            else:
                field_value = value.value_text

            options = []
            display_value = field_value

            if field.field_type in [
                "select",
                "radio",
                "checkbox",
            ]:
                options = [
                    {
                        "value": o.value,
                        "label_ar": o.label_ar,
                        "label_en": o.label_en,
                    }
                    for o in field.options.filter(
                        is_active=True
                    )
                ]

                selected = (
                    field_value
                    if isinstance(field_value, list)
                    else [field_value]
                )

                labels = []

                for selected_value in selected:
                    match = next(
                        (
                            opt
                            for opt in options
                            if opt["value"] == selected_value
                        ),
                        None,
                    )

                    labels.append(
                        match["label_ar"]
                        if match
                        else selected_value
                    )

                display_value = (
                    labels
                    if isinstance(field_value, list)
                    else labels[0]
                    if labels
                    else field_value
                )

            result.append({
                "field_id": field.id,
                "key": field.key,
                "system_key": field.system_key,
                "label_ar": field.label_ar,
                "label_en": field.label_en,
                "field_type": field.field_type,
                "value": field_value,
                "display_value": display_value,
                "options": options,
                "required": field.required,
            })

        return result