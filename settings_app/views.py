# settings_app/views.py
import smtplib
from django.core.mail import get_connection   # ✅ ADD
from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsAdminOrSuper
from .models import SiteSettings
from .serializers import SiteSettingsSerializer
from messaging.utils import load_smtp_settings  # ✅ ADD


# --------------------------------------------------
# 1) Site General Settings
# --------------------------------------------------
class SiteSettingsView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        settings = SiteSettings.objects.first()
        serializer = SiteSettingsSerializer(settings)
        return Response(serializer.data)

    def put(self, request):
        settings = SiteSettings.objects.first()
        serializer = SiteSettingsSerializer(
            settings,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


# --------------------------------------------------
# 2) Email SMTP Settings
# --------------------------------------------------
class EmailSettingsView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        settings = SiteSettings.objects.first()

        return Response({
            "smtp_host": settings.smtp_host,
            "smtp_port": settings.smtp_port,
            "smtp_username": settings.smtp_username,
            "smtp_password": settings.smtp_password,
            "smtp_use_tls": settings.smtp_use_tls,
            "smtp_use_ssl": settings.smtp_use_ssl,
            "contact_receiver_email": settings.contact_receiver_email,
            "auto_reply_email": settings.auto_reply_email,
        })

    def put(self, request):
        settings = SiteSettings.objects.first()

        fields = [
            "smtp_host", "smtp_port", "smtp_username", "smtp_password",
            "smtp_use_tls", "smtp_use_ssl",
            "contact_receiver_email", "auto_reply_email",
        ]

        for field in fields:
            if field in request.data:
                setattr(settings, field, request.data[field])

        settings.save()
        return Response({"success": True, "message": "Email settings updated"})


# --------------------------------------------------
# 3) Test SMTP Connection (✅ FIXED FOR REAL)
# --------------------------------------------------
class EmailSMTPTestView(APIView):
    permission_classes = [IsAdminOrSuper]

    def post(self, request):
        """
        اختبار اتصال SMTP الحقيقي باستخدام Django Email Backend
        """
        try:
            # تحميل إعدادات SMTP من قاعدة البيانات
            load_smtp_settings()

            # إنشاء اتصال فعلي (هذا يستدعي connect() داخليًا)
            connection = get_connection()
            connection.open()
            connection.close()

            return Response({"success": True})

        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=400
            )

