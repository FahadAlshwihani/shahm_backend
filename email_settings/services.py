from django.core.mail import (
    EmailMultiAlternatives,
)
from django.core.mail.backends.smtp import (
    EmailBackend,
)

from settings_app.models import (
    SiteSettings,
)


class DynamicEmailService:

    @staticmethod
    def get_backend():
        site = SiteSettings.objects.first()

        if not site:
            raise Exception(
                "Site settings not configured"
            )

        return EmailBackend(
            host=site.smtp_host,
            port=site.smtp_port,
            username=site.smtp_username,
            password=site.smtp_password,
            use_tls=site.smtp_use_tls,
            use_ssl=site.smtp_use_ssl,
            fail_silently=False,
        )

    @classmethod
    def send_email(
        cls,
        subject,
        body,
        recipient_list,
        html_body=None,
    ):
        site = SiteSettings.objects.first()

        if not site:
            raise Exception(
                "Site settings not configured"
            )

        backend = cls.get_backend()

        email = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=site.auto_reply_email,
            to=recipient_list,
            connection=backend,
        )

        if html_body:
            email.attach_alternative(
                html_body,
                "text/html",
            )

        email.send()