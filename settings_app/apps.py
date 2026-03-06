from django.apps import AppConfig

class SettingsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'settings_app'

    def ready(self):
        from .models import EmailTemplate

        default_templates = [
            ("auto_reply", "Auto Reply to Client"),
            ("subscription_welcome", "Subscription Welcome Email"),
            ("admin_alert", "Admin New Message Alert"),
        ]

        for t_type, _ in default_templates:
            EmailTemplate.objects.get_or_create(
                template_type=t_type,
                defaults={
                    "subject": "",
                    "html_content": "",
                }
            )
