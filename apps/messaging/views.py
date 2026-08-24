import csv

from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdminOrSuper
from apps.settings_app.models import SiteSettings

from .models import ContactMessage, Subscriber, BroadcastLog, EmailTemplate
from .serializers import (
    ContactMessageSerializer,
    SubscriberSerializer,
    BroadcastLogSerializer,
)
from .utils import render_email_template

from integrations.email.services import (
    DynamicEmailService,
)

# =========================
# Public Contact Form
# =========================
class ContactMessageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        message = serializer.save()

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
                "email": message.email or "",
                "phone": message.phone,
                "subject": message.subject,
                "message": message.message,
                "site_name": settings.site_name_ar,
            },
        )

        if subject and html and admin_email and sender_email:
            DynamicEmailService.send_email(
                subject=subject,
                body="",
                recipient_list=[admin_email],
                html_body=html,
            )

        # Auto reply only if email exists
        if message.email:
            subject, html = render_email_template(
                "auto_reply",
                {
                    "name": message.name,
                    "email": message.email,
                    "site_name": settings.site_name_ar,
                },
            )

            if subject and html and sender_email:
                DynamicEmailService.send_email(
                    subject=subject,
                    body="",
                    recipient_list=[message.email],
                    html_body=html,
                )

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

        settings = SiteSettings.objects.first()
        subject, html = render_email_template(
            "subscription_welcome",
            {
                "email": email,
                "site_name": settings.site_name_ar if settings else "",
            },
        )

        if subject and html and settings and settings.auto_reply_email:
            DynamicEmailService.send_email(
                subject=subject,
                body="",
                recipient_list=[email],
                html_body=html,
            )

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
            message = ContactMessage.objects.get(id=pk)
        except ContactMessage.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        if not message.is_read:
            message.is_read = True
            message.save(update_fields=["is_read"])

        serializer = ContactMessageSerializer(message)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            message = ContactMessage.objects.get(id=pk)
        except ContactMessage.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = ContactMessageSerializer(
            message,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# =========================
# Subscribers
# =========================
class SubscribersListView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        subs = Subscriber.objects.all()
        serializer = SubscriberSerializer(subs, many=True)
        return Response(serializer.data)


class SubscriberDeleteView(APIView):
    permission_classes = [IsAdminOrSuper]

    def delete(self, request, pk):
        try:
            sub = Subscriber.objects.get(id=pk)
            sub.delete()
            return Response({"success": True})
        except Subscriber.DoesNotExist:
            return Response({"error": "Subscriber not found"}, status=404)


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


        settings = SiteSettings.objects.first()
        sender = settings.auto_reply_email if settings else None

        if not sender:
            return Response(
                {"error": "Missing sender email in settings"},
                status=500
            )

        if subscriber_ids:
            qs = Subscriber.objects.filter(id__in=subscriber_ids)
        else:
            qs = Subscriber.objects.all()

        emails = list(qs.values_list("email", flat=True))

        sent = 0
        for email in emails:
            try:
                DynamicEmailService.send_email(
                    subject=subject,
                    body="",
                    recipient_list=[email],
                    html_body=html_content,
                )
                sent += 1
            except Exception:
                pass

        BroadcastLog.objects.create(
            subject=subject,
            html=html_content,
            recipients_count=sent,
            recipients_list="\n".join(emails),
        )

        return Response({"success": True, "sent": sent})


class BroadcastLogsListView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        logs = BroadcastLog.objects.all()
        serializer = BroadcastLogSerializer(logs, many=True)
        return Response(serializer.data)


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
