from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsEditorOrAbove

from .client_files import Client, ClientFile
from .serializers import ClientSerializer, ClientFileSerializer


class AdminClientsView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        return Response(ClientSerializer(Client.objects.all(), many=True).data)


class AdminClientFilesView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request, pk):
        files = ClientFile.objects.filter(client_id=pk)
        return Response(ClientFileSerializer(files, many=True).data)

    def post(self, request, pk):
        serializer = ClientFileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(client_id=pk)
        return Response(serializer.data)
