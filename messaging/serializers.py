from rest_framework import serializers
from .models import ContactMessage, Subscriber, BroadcastLog


class ContactMessageSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = ContactMessage
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_read",
        ]

    def validate_phone(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Phone is required.")
        return value

    def validate_email(self, value):
        if value in ("", None):
            return None
        return value


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class BroadcastLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]