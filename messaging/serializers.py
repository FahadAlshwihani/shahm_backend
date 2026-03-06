from rest_framework import serializers
from .models import ContactMessage, Subscriber, BroadcastLog


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "is_read",
        ]


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
