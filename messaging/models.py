from django.db import models


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("closed", "Closed"),
    ]

    name = models.CharField(max_length=150, blank=True)
    subject = models.CharField(max_length=250, blank=True)
    message = models.TextField(blank=True)

    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new"
    )
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        display_name = self.name or "Unknown"
        return f"Message from {display_name}"

    class Meta:
        ordering = ["-created_at"]


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ["-created_at"]


class BroadcastLog(models.Model):
    subject = models.CharField(max_length=300)
    html = models.TextField()
    recipients_count = models.IntegerField(default=0)
    recipients_list = models.TextField()   # تخزين الإيميلات كنص مفصول بفواصل أو أسطر
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Broadcast: {self.subject} ({self.created_at.date()})"

    class Meta:
        ordering = ["-created_at"]

class EmailTemplate(models.Model):
    TEMPLATE_CHOICES = [
        ("admin_alert", "Admin Alert"),
        ("auto_reply", "Auto Reply"),
        ("subscription_welcome", "Subscription Welcome"),
    ]

    template_type = models.CharField(
        max_length=50,
        choices=TEMPLATE_CHOICES,
        unique=True
    )
    subject = models.CharField(max_length=255, blank=True)
    html_content = models.TextField()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.template_type
