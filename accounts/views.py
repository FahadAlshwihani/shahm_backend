from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import UserSerializer
from accounts.permissions import IsAdminOrSuper


# ----------------------------------
# 1) Create first super admin
# ----------------------------------
class FirstAdminSetupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        if User.objects.exists():
            return Response({"error": "Setup already completed."}, status=403)

        data = request.data.copy()
        data["role"] = "super_admin"
        data["is_active"] = True
        data["is_staff"] = True
        data["is_superuser"] = True

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                "success": True,
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })

        return Response(serializer.errors, status=400)


# ----------------------------------
# 2) Login (JWT)
# ----------------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            return Response({"error": "Invalid email or password"}, status=400)

        if not user.is_active:
            return Response({"error": "Account disabled"}, status=403)

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


# ----------------------------------
# 3) Admin: Manage Users
# ----------------------------------
class UsersListView(APIView):
    permission_classes = [IsAdminOrSuper]

    def get(self, request):
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data)


class CreateUserView(APIView):
    permission_classes = [IsAdminOrSuper]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)


class UserDetailView(APIView):
    permission_classes = [IsAdminOrSuper]

    def patch(self, request, pk):
        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user = get_object_or_404(User, id=pk)
        user.delete()
        return Response({"success": True}, status=200)
