from rest_framework.views import APIView
from rest_framework.response import Response
from core.permissions import IsAdminOrSuper

from settings_app.models import SiteSettings
from .serializers import EmailSettingsSerializer

class EmailSettingsView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        settings = SiteSettings.objects.first()
        serializer = EmailSettingsSerializer(settings)
        return Response(serializer.data)

    def put(self, request):
        settings = SiteSettings.objects.first()
        serializer = EmailSettingsSerializer(settings, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)
