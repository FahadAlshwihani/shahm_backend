# team/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .models import TeamMember
from .serializers import TeamMemberSerializer
from accounts.permissions import IsEditorOrAbove
from .models import TeamPage
from .serializers import TeamPageSerializer


# -------- PUBLIC --------
class PublicTeamView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        members = TeamMember.objects.filter(is_active=True).order_by("order")
        serializer = TeamMemberSerializer(
            members, many=True, context={"request": request}
        )
        return Response(serializer.data)


# -------- ADMIN LIST / CREATE --------
class TeamListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        members = TeamMember.objects.all().order_by("order")
        serializer = TeamMemberSerializer(
            members, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = TeamMemberSerializer(
            data=request.data,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)


# -------- ADMIN DETAIL --------
class TeamDetailView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request, pk):
        try:
            member = TeamMember.objects.get(id=pk)
        except TeamMember.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = TeamMemberSerializer(
            member,
            context={"request": request}
        )
        return Response(serializer.data)

    def patch(self, request, pk):
        try:
            member = TeamMember.objects.get(id=pk)
        except TeamMember.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        serializer = TeamMemberSerializer(
            member,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        try:
            member = TeamMember.objects.get(id=pk)
        except TeamMember.DoesNotExist:
            return Response({"detail": "Not found"}, status=404)

        member.delete()
        return Response(status=204)

class PublicTeamPageView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = TeamPage.objects.first()
        serializer = TeamPageSerializer(page)
        return Response(serializer.data)


# -------- ADMIN TEAM PAGE --------
class TeamPageAdminView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrAbove]

    def get(self, request):
        page = TeamPage.objects.first()
        serializer = TeamPageSerializer(page)
        return Response(serializer.data)

    def post(self, request):
        page, _ = TeamPage.objects.get_or_create(id=1)

        serializer = TeamPageSerializer(
            page,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)

