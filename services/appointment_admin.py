from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

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

from services.appointment import (
    AppointmentSlotSerializer,
    AppointmentBookingSerializer,
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
        slots = AppointmentSlot.objects.order_by("date", "start_time")
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
        bookings = AppointmentBooking.objects.select_related("slot").order_by("-created_at")

        serializer = AppointmentBookingSerializer(
            bookings,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data)


class AdminGenerateSlotsView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def post(self, request):
        date_str = request.data.get("date")
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")
        duration = int(request.data.get("duration", 60))

        if not date_str or not start_time or not end_time:
            return Response(
                {"detail": "date, start_time, end_time and shift are required"},
                status=400
            )

        try:
            slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start = datetime.strptime(start_time, "%H:%M").time()
            end = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
            return Response(
                {"detail": "Invalid date/time format"},
                status=400
            )

        if duration <= 0:
            return Response(
                {"detail": "Duration must be greater than zero"},
                status=400
            )

        if slot_date < datetime.now().date():
            return Response(
                {"detail": "Cannot generate slots in the past"},
                status=400
            )

        current = datetime.combine(slot_date, start)
        end_dt = datetime.combine(slot_date, end)

        if current >= end_dt:
            return Response(
                {"detail": "End time must be after start time"},
                status=400
            )

        created = []
        skipped = []

        while current < end_dt:
            slot_end = current + timedelta(minutes=duration)

            if slot_end > end_dt:
                break

            exists = AppointmentSlot.objects.filter(
                date=slot_date,
                start_time=current.time(),
            ).exists()

            slot_shift = (
                "morning"
                if current.time().hour < 12
                else "evening"
            )

            if exists:
                skipped.append({
                    "start_time": current.time(),
                    "end_time": slot_end.time(),
                    "shift": slot_shift,
                    "reason": "duplicate"
                })
            else:
                slot = AppointmentSlot.objects.create(
                    date=slot_date,
                    start_time=current.time(),
                    end_time=slot_end.time(),
                    shift=slot_shift,
                    is_available=True
                )
                created.append(slot.id)

            current = slot_end

        return Response({
            "created_slots": created,
            "skipped_slots": skipped
        })


class AdminCancelBookingView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        booking = get_object_or_404(AppointmentBooking, id=pk)

        if booking.status == "cancelled":
            return Response({"detail": "Booking already cancelled"}, status=400)

        booking.status = "cancelled"
        booking.save(update_fields=["status"])

        if booking.slot_id:
            AppointmentSlot.objects.filter(
                id=booking.slot_id
            ).update(
                is_available=True
            )
        return Response({"status": "cancelled"})


class AdminUpdateBookingStatusView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        booking = get_object_or_404(AppointmentBooking, id=pk)
        status_value = request.data.get("status")

        if status_value not in ["pending", "confirmed", "cancelled"]:
            return Response({"detail": "Invalid status"}, status=400)

        booking.status = status_value
        booking.save(update_fields=["status"])

        if booking.slot_id:
            AppointmentSlot.objects.filter(
                id=booking.slot_id
            ).update(
                is_available=(
                        status_value == "cancelled"
                )
            )

        return Response({"success": True})
