from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .models import LegalPage
from .serializers import LegalPageSerializer
from accounts.permissions import IsEditorOrAbove, IsAdminOrSuper


# ------------------------------------
# Public: عرض صفحة قانونية
# ------------------------------------
class PublicLegalPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        try:
            page = LegalPage.objects.get(slug=slug, is_published=True)
        except LegalPage.DoesNotExist:
            return Response({"detail": "Page not found"}, status=404)

        serializer = LegalPageSerializer(page)
        return Response(serializer.data)


# ------------------------------------
# Dashboard: إدارة الصفحات القانونية
# ------------------------------------

class LegalPageListCreateView(APIView):
    # Editor + Admin + Super Admin
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        pages = LegalPage.objects.all()
        serializer = LegalPageSerializer(pages, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LegalPageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class LegalPageDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request, pk):
        try:
            page = LegalPage.objects.get(id=pk)
        except LegalPage.DoesNotExist:
            return Response({"detail": "Page not found"}, status=404)

        serializer = LegalPageSerializer(page)
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            page = LegalPage.objects.get(id=pk)
        except LegalPage.DoesNotExist:
            return Response({"detail": "Page not found"}, status=404)

        serializer = LegalPageSerializer(page, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            page = LegalPage.objects.get(id=pk)
        except LegalPage.DoesNotExist:
            return Response({"detail": "Page not found"}, status=404)

        page.delete()
        return Response(status=204)
