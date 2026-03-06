from rest_framework import serializers
from settings_app.models import SiteSettings

class EmailSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "smtp_host",
            "smtp_port",
            "smtp_username",
            "smtp_password",
            "use_tls",
            "use_ssl",
            "sender_email",
            "admin_email",
            "customer_reply_template",
            "admin_notify_template",
        ]
