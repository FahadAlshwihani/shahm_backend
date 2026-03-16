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

from services.utils import generate_reference


from services.appointment import (
    AppointmentSlotSerializer,
    AppointmentBookingSerializer,
)



class BookAppointmentView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [
        JSONParser,
        MultiPartParser,
        FormParser
    ]
    def post(self, request):

        slot_id = request.data.get("slot")

        if not slot_id:
            return Response(
                {"detail": "Slot required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            slot = AppointmentSlot.objects.get(
                id=slot_id,
                is_available=True
            )
        except AppointmentSlot.DoesNotExist:
            return Response(
                {"detail": "Slot not available"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # منع المواعيد الماضية
        slot_datetime = timezone.make_aware(
            datetime.combine(slot.date, slot.start_time),
            timezone.get_current_timezone()
        )

        if slot_datetime <= timezone.localtime():
            return Response(
                {"detail": "This slot has already passed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # منع double booking
        if AppointmentBooking.objects.filter(slot=slot).exists():
            return Response(
                {"detail": "Slot already booked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AppointmentBookingSerializer(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    slot = AppointmentSlot.objects.select_for_update().get(
                        id=slot_id,
                        is_available=True
                    )

                    if AppointmentBooking.objects.filter(slot=slot).exists():
                        return Response(
                            {"detail": "Slot already booked"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    booking = serializer.save(
                        slot=slot,
                        status="pending"
                    )

                    booking.reference = generate_reference("booking")
                    booking.save(update_fields=["reference"])

                    slot.is_available = False
                    slot.save(update_fields=["is_available"])

            except AppointmentSlot.DoesNotExist:
                return Response(
                    {"detail": "Slot not available"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except IntegrityError:
                return Response(
                    {"detail": "Slot already booked"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {
                    "booking_id": booking.id,
                    "message": "Appointment booked successfully"
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
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
            is_available=True
        )

        if date:
            qs = qs.filter(date=date)

        if period in ["morning", "evening"]:
            qs = qs.filter(shift=period)

        qs = qs.exclude(date=today, start_time__lte=now_time)
        qs = qs.order_by("date", "start_time")

        serializer = AppointmentSlotSerializer(qs, many=True)
        return Response(serializer.data)