from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from services.models import (
    AppointmentPage,
    AppointmentSettings,
    AppointmentSlot,
    AppointmentBooking,
)
from services.appointment_cms import (
    AppointmentPageSerializer,
    AppointmentSettingsSerializer,
)

from accounts.permissions import IsEditorOrAbove


# ===============================
# CMS PAGE
# ===============================
class AdminAppointmentPageView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        page, _ = AppointmentPage.objects.get_or_create(id=1)
        return Response(AppointmentPageSerializer(page).data)

    def patch(self, request):
        page, _ = AppointmentPage.objects.get_or_create(id=1)
        serializer = AppointmentPageSerializer(
            page, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ===============================
# SETTINGS
# ===============================
class AdminAppointmentSettingsView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        settings, _ = AppointmentSettings.objects.get_or_create(id=1)
        return Response(AppointmentSettingsSerializer(settings).data)

    def patch(self, request):
        settings, _ = AppointmentSettings.objects.get_or_create(id=1)
        serializer = AppointmentSettingsSerializer(
            settings, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdminAppointmentSlotsView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        slots = AppointmentSlot.objects.all().order_by("date", "start_time")
        serializer = AppointmentSlotSerializer(slots, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AppointmentSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(is_available=True)
        return Response(serializer.data, status=201)



class AdminAppointmentSlotDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        slot = get_object_or_404(AppointmentSlot, id=pk)
        serializer = AppointmentSlotSerializer(
            slot, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        slot = get_object_or_404(AppointmentSlot, id=pk)
        slot.delete()
        return Response(status=204)



class AdminAppointmentBookingsView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        bookings = AppointmentBooking.objects.select_related(
            "slot"
        ).order_by("-created_at")

        serializer = AppointmentBookingSerializer(bookings, many=True)
        return Response(serializer.data)
