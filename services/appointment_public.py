from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.utils import timezone
from django.db import IntegrityError, transaction
from datetime import datetime
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from services.models import (
    AppointmentSlot,
    AppointmentBooking,
    AppointmentPage,
    AppointmentSettings,
)

from services.appointment_cms import (
    AppointmentPageSerializer,
    AppointmentSettingsSerializer,
)

from services.utils.references import (
    generate_reference,
)

from services.appointment import (
    AppointmentSlotSerializer,
    AppointmentBookingSerializer,
)


class PublicAppointmentPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = AppointmentPage.objects.first()
        return Response(
            AppointmentPageSerializer(page).data if page else {}
        )


class PublicAppointmentSettingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        settings = AppointmentSettings.objects.filter(is_active=True).first()
        return Response(
            AppointmentSettingsSerializer(settings).data if settings else {}
        )


class PublicAvailableSlotsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        period = request.query_params.get("period")
        date = request.query_params.get("date")

        today = timezone.localdate()
        now_time = timezone.localtime().time()

        qs = AppointmentSlot.objects.filter(
            date__gte=today,
        )

        if date:
            qs = qs.filter(date=date)

        if period in ["morning", "evening"]:
            qs = qs.filter(shift=period)

        qs = qs.exclude(date=today, start_time__lte=now_time)
        qs = qs.order_by("date", "start_time")

        serializer = AppointmentSlotSerializer(
            qs,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)
