from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.http import FileResponse
from django.shortcuts import get_object_or_404
import mimetypes


from .models import PracticeArea, Service, ServiceAdvisoryPage, CareerJob, CareerApplication
from .serializers import PracticeAreaSerializer, ServiceSerializer, ServiceAdvisoryPageSerializer, ServiceAdvisoryRequestSerializer, ServiceAdvisoryRequest, CareerJobSerializer, CareerApplicationSerializer
from accounts.permissions import IsEditorOrAbove


# ---------------- PUBLIC ----------------
class PublicPracticeAreasView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        areas = PracticeArea.objects.filter(is_active=True).order_by("order")
        serializer = PracticeAreaSerializer(areas, many=True)
        return Response(serializer.data)


# ---------------- ADMIN: Areas ----------------
class PracticeAreaListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        areas = PracticeArea.objects.all().order_by("order")
        serializer = PracticeAreaSerializer(areas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PracticeAreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class PracticeAreaDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        try:
            area = PracticeArea.objects.get(id=pk)
        except PracticeArea.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = PracticeAreaSerializer(area, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            area = PracticeArea.objects.get(id=pk)
        except PracticeArea.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        area.delete()
        return Response(status=204)


# ---------------- ADMIN: Services ----------------
class ServiceListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        items = Service.objects.all().order_by("order")
        serializer = ServiceSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ServiceDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        try:
            item = Service.objects.get(id=pk)
        except Service.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = ServiceSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            item = Service.objects.get(id=pk)
        except Service.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        item.delete()
        return Response(status=204)

# ---------------------------------------------------------
# Public Practice Area Details (with services)
# ---------------------------------------------------------
class PublicPracticeAreaDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            area = PracticeArea.objects.get(slug=slug, is_active=True)
        except PracticeArea.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        # Bring all related services
        services = Service.objects.filter(practice_area=area, is_active=True)

        data = PracticeAreaSerializer(area, context={"request": request}).data
        data["services"] = ServiceSerializer(services, many=True, context={"request": request}).data

        return Response(data)


class PublicServiceAdvisoryPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = ServiceAdvisoryPage.objects.first()
        serializer = ServiceAdvisoryPageSerializer(page)
        return Response(serializer.data if page else {})


class AdminServiceAdvisoryPageView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        page, _ = ServiceAdvisoryPage.objects.get_or_create(id=1)
        return Response(ServiceAdvisoryPageSerializer(page).data)

    def post(self, request):
        page, _ = ServiceAdvisoryPage.objects.get_or_create(id=1)
        serializer = ServiceAdvisoryPageSerializer(
            page, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SubmitServiceAdvisoryRequest(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = ServiceAdvisoryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True})


class AdminServiceAdvisoryRequestsView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        qs = ServiceAdvisoryRequest.objects.all().order_by("-created_at")
        serializer = ServiceAdvisoryRequestSerializer(qs, many=True)
        return Response(serializer.data)


# views.py
class AdminServiceAdvisoryRequestDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        try:
            item = ServiceAdvisoryRequest.objects.get(id=pk)
        except ServiceAdvisoryRequest.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = ServiceAdvisoryRequestSerializer(
            item, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PublicServicesListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Service.objects.filter(is_active=True).order_by("order")
        serializer = ServiceSerializer(qs, many=True)
        return Response(serializer.data)



class AdminServiceAdvisoryDownloadView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request, pk):
        item = get_object_or_404(ServiceAdvisoryRequest, id=pk)

        if not item.attachment:
            return Response({"detail": "No file"}, status=404)

        file_path = item.attachment.path
        mime_type, _ = mimetypes.guess_type(file_path)

        response = FileResponse(
            open(file_path, "rb"),
            content_type=mime_type or "application/octet-stream",
        )
        response["Content-Disposition"] = f'attachment; filename="{item.attachment.name.split("/")[-1]}"'
        return response


# =========================================================
# ================= CAREERS VIEWS ==========================
# =========================================================

# ---------- PUBLIC JOBS ----------
class PublicCareerJobsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        jobs = CareerJob.objects.filter(is_active=True)
        return Response(CareerJobSerializer(jobs, many=True).data)


# ---------- SUBMIT APPLICATION ----------
class SubmitCareerApplication(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CareerApplicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True})


# ---------- ADMIN JOBS ----------
class AdminCareerJobsView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        jobs = CareerJob.objects.all()
        return Response(CareerJobSerializer(jobs, many=True).data)

    def post(self, request):
        serializer = CareerJobSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class AdminCareerJobDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def patch(self, request, pk):
        job = get_object_or_404(CareerJob, id=pk)
        serializer = CareerJobSerializer(job, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        CareerJob.objects.filter(id=pk).delete()
        return Response(status=204)


# ---------- ADMIN APPLICATIONS ----------
class AdminCareerApplicationsView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        apps = CareerApplication.objects.all().order_by("-created_at")
        return Response(CareerApplicationSerializer(apps, many=True).data)


class PublicServiceDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        service = get_object_or_404(Service, slug=slug, is_active=True)

        serializer = ServiceSerializer(
            service,
            context={"request": request}
        )

        return Response(serializer.data)