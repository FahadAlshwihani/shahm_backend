from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse



from settings_app.models import SiteSettings
from core.permissions import IsAdminOrSuper


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse


from settings_app.models import SiteSettings
from core.permissions import IsAdminOrSuper


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
import csv

from .models import (
    ContactMessage,
    Subscriber,
    BroadcastLog,
    EmailTemplate,
)
from .serializers import (
    ContactMessageSerializer,
    SubscriberSerializer,
    BroadcastLogSerializer,
)
from settings_app.models import SiteSettings
from core.permissions import IsAdminOrSuper
from .utils import load_smtp_settings, render_email_template


# =========================
# Public Contact Form
# =========================
class ContactMessageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        message = serializer.save()
        load_smtp_settings()

        settings = SiteSettings.objects.first()
        if not settings:
            return Response({"success": True})

        sender_email = settings.auto_reply_email
        admin_email = settings.contact_receiver_email

        # Admin alert
        subject, html = render_email_template(
            "admin_alert",
            {
                "name": message.name,
                "email": message.email,
                "phone": message.phone,
                "subject": message.subject,
                "message": message.message,
                "site_name": settings.site_name_ar,
            },
        )

        if subject and html and admin_email:
            mail = EmailMultiAlternatives(
                subject=subject,
                body="",
                from_email=sender_email,
                to=[admin_email],
            )
            mail.attach_alternative(html, "text/html")
            mail.send()

        # Auto reply
        subject, html = render_email_template(
            "auto_reply",
            {
                "name": message.name,
                "email": message.email,
                "site_name": settings.site_name_ar,
            },
        )

        if subject and html:
            mail = EmailMultiAlternatives(
                subject=subject,
                body="",
                from_email=sender_email,
                to=[message.email],
            )
            mail.attach_alternative(html, "text/html")
            mail.send()

        return Response({"success": True})


# =========================
# Newsletter Subscribe
# =========================
class SubscriberView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email required"}, status=400)

        if Subscriber.objects.filter(email=email).exists():
            return Response({"success": True})

        Subscriber.objects.create(email=email)
        load_smtp_settings()

        settings = SiteSettings.objects.first()
        subject, html = render_email_template(
            "subscription_welcome",
            {
                "email": email,
                "site_name": settings.site_name_ar if settings else "",
            },
        )

        if subject and html and settings and settings.auto_reply_email:
            mail = EmailMultiAlternatives(
                subject=subject,
                body="",
                from_email=settings.auto_reply_email,
                to=[email],
            )
            mail.attach_alternative(html, "text/html")
            mail.send()

        return Response({"success": True})


# =========================
# Admin Messages List
# =========================
class AdminMessagesView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        qs = ContactMessage.objects.all()
        return Response(ContactMessageSerializer(qs, many=True).data)


# =========================
# Admin Single Message
# =========================
class AdminSingleMessageView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request, pk):
        try:
            msg = ContactMessage.objects.get(pk=pk)
        except ContactMessage.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        if not msg.is_read:
            msg.is_read = True
            msg.save()

        return Response(ContactMessageSerializer(msg).data)


# =========================
# Subscribers
# =========================
class SubscribersListView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        qs = Subscriber.objects.all()
        return Response(SubscriberSerializer(qs, many=True).data)


class SubscriberDeleteView(APIView):
    permission_classes = [IsAdminOrSuper]

    def delete(self, request, pk):
        Subscriber.objects.filter(pk=pk).delete()
        return Response({"success": True})


class ExportSubscribersCSV(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=subscribers.csv"
        writer = csv.writer(response)
        writer.writerow(["Email", "Created At"])
        for s in Subscriber.objects.all():
            writer.writerow([s.email, s.created_at])
        return response


# =========================
# Broadcast
# =========================
class BroadcastEmailView(APIView):
    permission_classes = [IsAdminOrSuper]

    def post(self, request):
        subject = request.data.get("subject")
        html = request.data.get("html")

        if not subject or not html:
            return Response({"error": "Missing fields"}, status=400)

        load_smtp_settings()
        settings = SiteSettings.objects.first()
        sender = settings.auto_reply_email

        emails = Subscriber.objects.values_list("email", flat=True)
        sent = 0

        for email in emails:
            mail = EmailMultiAlternatives(
                subject=subject,
                body="",
                from_email=sender,
                to=[email],
            )
            mail.attach_alternative(html, "text/html")
            mail.send()
            sent += 1

        BroadcastLog.objects.create(
            subject=subject,
            html=html,
            recipients_count=sent,
            recipients_list="\n".join(emails),
        )

        return Response({"success": True, "sent": sent})


class BroadcastLogsListView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        qs = BroadcastLog.objects.all()
        return Response(BroadcastLogSerializer(qs, many=True).data)


# =========================
# Email Templates (Admin)
# =========================
class EmailTemplateView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        return Response([
            {
                "template_type": t.template_type,
                "subject": t.subject,
                "html_content": t.html_content,
            }
            for t in EmailTemplate.objects.all()
        ])

    def post(self, request):
        EmailTemplate.objects.update_or_create(
            template_type=request.data["template_type"],
            defaults={
                "subject": request.data.get("subject", ""),
                "html_content": request.data["html_content"],
            },
        )
        return Response({"success": True})

# =========================
# Admin Single Message
# =========================
class AdminSingleMessageView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request, pk):
        try:
            message = ContactMessage.objects.get(id=pk)
        except ContactMessage.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        if not message.is_read:
            message.is_read = True
            message.save()

        serializer = ContactMessageSerializer(message)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            message = ContactMessage.objects.get(id=pk)
        except ContactMessage.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = ContactMessageSerializer(
            message, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


# =========================
# Admin Subscribers List
# =========================
class SubscribersListView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        subs = Subscriber.objects.all()
        serializer = SubscriberSerializer(subs, many=True)
        return Response(serializer.data)


# =========================
# Admin Delete Subscriber
# =========================
class SubscriberDeleteView(APIView):
    permission_classes = [IsAdminOrSuper]

    def delete(self, request, pk):
        try:
            sub = Subscriber.objects.get(id=pk)
            sub.delete()
            return Response({"success": True})
        except Subscriber.DoesNotExist:
            return Response({"error": "Subscriber not found"}, status=404)


# =========================
# Export Subscribers CSV
# =========================
class ExportSubscribersCSV(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=subscribers.csv"

        writer = csv.writer(response)
        writer.writerow(["ID", "Email", "Created At"])

        for sub in Subscriber.objects.all():
            writer.writerow([sub.id, sub.email, sub.created_at])

        return response


# =========================
# Broadcast Email + LOG
# =========================
class BroadcastEmailView(APIView):
    permission_classes = [IsAdminOrSuper]

    def post(self, request):
        subject = request.data.get("subject")
        html_content = request.data.get("html")
        subscriber_ids = request.data.get("subscriber_ids", None)

        if not subject or not html_content:
            return Response({"error": "Missing fields"}, status=400)

        # تحميل SMTP
        load_smtp_settings()

        settings = SiteSettings.objects.first()
        sender = settings.auto_reply_email if settings else None

        if not sender:
            return Response(
                {"error": "Missing sender email in settings"}, status=500
            )

        # اختيار المستلمين
        if subscriber_ids:
            qs = Subscriber.objects.filter(id__in=subscriber_ids)
        else:
            qs = Subscriber.objects.all()

        emails = list(qs.values_list("email", flat=True))

        sent = 0
        for email in emails:
            try:
                mail = EmailMultiAlternatives(
                    subject=subject,
                    body="",
                    from_email=sender,
                    to=[email],
                )
                mail.attach_alternative(html_content, "text/html")
                mail.send()
                sent += 1
            except Exception as e:
                print(f"Email error for {email}: {e}")

        # حفظ سجل الإرسال
        BroadcastLog.objects.create(
            subject=subject,
            html=html_content,
            recipients_count=sent,
            recipients_list="\n".join(emails),
        )

        return Response({"success": True, "sent": sent})


# =========================
# Broadcast Logs List
# =========================
class BroadcastLogsListView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        logs = BroadcastLog.objects.all()
        serializer = BroadcastLogSerializer(logs, many=True)
        return Response(serializer.data)
