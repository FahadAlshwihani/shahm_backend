from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import LegalPage
from .serializers import LegalPageSerializer, PublicLegalPageSerializer
from accounts.permissions import IsEditorOrAbove


class PublicLegalPageView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, slug):

        page = get_object_or_404(
            LegalPage.objects.prefetch_related("sections__subsections"),
            slug=slug,
            is_published=True
        )

        serializer = PublicLegalPageSerializer(page)

        return Response(serializer.data)


class LegalPageListCreateView(APIView):

    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):

        pages = LegalPage.objects.prefetch_related("sections__subsections")

        serializer = LegalPageSerializer(pages, many=True)

        return Response(serializer.data)

    def post(self, request):

        serializer = LegalPageSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data, status=201)


class LegalPageDetailView(APIView):

    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get_object(self, pk):

        return get_object_or_404(
            LegalPage.objects.prefetch_related("sections__subsections"),
            pk=pk
        )

    def get(self, request, pk):

        page = self.get_object(pk)

        serializer = LegalPageSerializer(page)

        return Response(serializer.data)

    def patch(self, request, pk):

        page = self.get_object(pk)

        serializer = LegalPageSerializer(
            page,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(serializer.data)

    def delete(self, request, pk):

        page = self.get_object(pk)

        page.delete()

        return Response(status=204)