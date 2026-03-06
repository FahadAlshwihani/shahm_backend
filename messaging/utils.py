from django.conf import settings as django_settings
from settings_app.models import SiteSettings
from .models import EmailTemplate


def load_smtp_settings():
    config = SiteSettings.objects.first()
    if not config:
        return

    django_settings.EMAIL_HOST = config.smtp_host
    django_settings.EMAIL_PORT = config.smtp_port
    django_settings.EMAIL_HOST_USER = config.smtp_username
    django_settings.EMAIL_HOST_PASSWORD = config.smtp_password
    django_settings.EMAIL_USE_TLS = config.smtp_use_tls
    django_settings.EMAIL_USE_SSL = config.smtp_use_ssl


def render_email_template(template_type, context):
    tpl = EmailTemplate.objects.filter(template_type=template_type).first()
    if not tpl:
        return None, None

    html = tpl.html_content
    for k, v in context.items():
        html = html.replace(f"{{{{{k}}}}}", v or "")

    return tpl.subject, html
