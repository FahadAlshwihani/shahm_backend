# settings_app/models.py
from django.db import models

class SiteSettings(models.Model):

    # -----------------------
    # معلومات عامة
    # -----------------------
    site_name_ar = models.CharField(max_length=200, default="شهم للمحاماة")
    site_name_en = models.CharField(max_length=200, default="Shahm Law Firm")

    # -----------------------
    # البريد الخاص بالتنبيهات
    # -----------------------
    contact_receiver_email = models.EmailField(default="", blank=True)
    auto_reply_email = models.EmailField(default="", blank=True)

    # -----------------------
    # إعدادات SMTP
    # -----------------------
    smtp_host = models.CharField(max_length=200, blank=True)
    smtp_port = models.IntegerField(default=587)
    smtp_username = models.CharField(max_length=200, blank=True)
    smtp_password = models.CharField(max_length=200, blank=True)

    smtp_use_tls = models.BooleanField(default=True)
    smtp_use_ssl = models.BooleanField(default=False)

    # -----------------------
    # قوالب HTML
    # -----------------------
    customer_reply_template = models.TextField(blank=True)
    admin_notify_template = models.TextField(blank=True)

    # -----------------------
    # معلومات التواصل (تُستخدم في الفوتر)
    # -----------------------
    phone_number = models.CharField(max_length=50, blank=True)
    whatsapp_number = models.CharField(max_length=50, blank=True)

    # -----------------------
    # الروابط الاجتماعية (لعمود "تابعنا")
    # -----------------------
    linkedin_url = models.URLField(blank=True)
    x_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)

    # -----------------------
    # الشعار
    # -----------------------
    logo_light = models.ImageField(upload_to="logo/", blank=True, null=True)
    logo_dark = models.ImageField(upload_to="logo/", blank=True, null=True)

    # -----------------------
    # الدولة واللغة (للفوتر: البلد/المنطقة)
    # -----------------------
    country = models.CharField(max_length=100, default="Saudi Arabia")
    locale = models.CharField(max_length=20, default="ar")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Site Settings"

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

