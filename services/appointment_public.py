from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from services.models import AppointmentSlot, AppointmentPage, AppointmentSettings, AppointmentSlot
from services.appointment_cms import (
    AppointmentPageSerializer,
    AppointmentSettingsSerializer,
)

from services.utils import generate_reference


from services.appointment import (
    AppointmentSlotSerializer,
    AppointmentBookingSerializer,
)



class AvailableAppointmentSlotsView(APIView):
    def get(self, request):
        slots = AppointmentSlot.objects.filter(is_available=True)
        serializer = AppointmentSlotSerializer(slots, many=True)
        return Response(serializer.data)



class BookAppointmentView(APIView):
    def post(self, request):
        slot_id = request.data.get("slot")

        # 1️⃣ تأكد أن الموعد موجود ومتاح
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

        # 2️⃣ أنشئ الحجز
        serializer = AppointmentBookingSerializer(data=request.data)


        if serializer.is_valid():
            booking = serializer.save(
                slot=slot,
                status="pending"
            )
            booking.reference = generate_reference("booking")
            booking.save()

            return Response(
                {
                    "booking_id": booking.id,
                    "message": "Appointment booked, awaiting payment"
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
        slots = AppointmentSlot.objects.filter(is_available=True)
        serializer = AppointmentSlotSerializer(slots, many=True)
        return Response(serializer.data)