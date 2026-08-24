from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "site_name_ar",
        "site_name_en",
        "contact_receiver_email",
        "auto_reply_email",
        "country",
        "locale",
        "updated_at",
    )

    readonly_fields = (
        "updated_at",
    )

    fieldsets = (
        (
            "General Information",
            {
                "fields": (
                    "site_name_ar",
                    "site_name_en",
                    "country",
                    "locale",
                )
            },
        ),

        (
            "Email Addresses",
            {
                "fields": (
                    "contact_receiver_email",
                    "auto_reply_email",
                )
            },
        ),

        (
            "SMTP Configuration",
            {
                "fields": (
                    "smtp_host",
                    "smtp_port",
                    "smtp_username",
                    "smtp_password",
                    "smtp_use_tls",
                    "smtp_use_ssl",
                )
            },
        ),

        (
            "Email Templates",
            {
                "fields": (
                    "customer_reply_template",
                    "admin_notify_template",
                )
            },
        ),

        (
            "Contact Information",
            {
                "fields": (
                    "phone_number",
                    "whatsapp_number",
                )
            },
        ),

        (
            "Social Media",
            {
                "fields": (
                    "linkedin_url",
                    "x_url",
                    "instagram_url",
                    "tiktok_url",
                )
            },
        ),

        (
            "Logos",
            {
                "fields": (
                    "logo_light",
                    "logo_dark",
                )
            },
        ),

        (
            "System",
            {
                "fields": (
                    "updated_at",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()