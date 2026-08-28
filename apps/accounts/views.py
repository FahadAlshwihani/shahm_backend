import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken

from . import login_lockout
from .guards import leaves_no_active_super_admin
from .models import User
from .roles import can_administer
from .serializers import UserSerializer
from apps.accounts.permissions import IsAdminOrSuper

logger = logging.getLogger("shahm.accounts")


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

        serializer = UserSerializer(
            data=data,
            context={"bootstrap": True},
        )
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
    throttle_scope = "login"

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Invalid email or password"}, status=401)

        if login_lockout.is_locked(email):
            logger.warning("Sign-in blocked for a locked account")
            return Response(
                {"error": "Too many failed attempts. Try again later."},
                status=429,
            )

        # authenticate() hashes a dummy password when no account matches, so a
        # wrong address and a wrong password take the same time to answer and
        # cannot be told apart by the caller.
        user = authenticate(request, email=email, password=password)

        if user is None:
            if self._is_disabled_account(email, password):
                return Response({"error": "Account disabled"}, status=403)

            attempts = login_lockout.register_failure(email)
            logger.warning("Failed sign-in attempt number %s", attempts)

            return Response({"error": "Invalid email or password"}, status=401)

        login_lockout.clear(email)

        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })

    @staticmethod
    def _is_disabled_account(email, password):
        """Keep the historical 403 answer for a correct but disabled login."""
        candidate = User.objects.filter(email=email).first()

        return bool(
            candidate
            and not candidate.is_active
            and candidate.check_password(password)
        )


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
        serializer = UserSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=201)
        return Response(serializer.errors, status=400)


class UserDetailView(APIView):
    permission_classes = [IsAdminOrSuper]

    def patch(self, request, pk):
        user = get_object_or_404(User, id=pk)

        if not can_administer(request.user, user):
            return Response(
                {"error": "You may not manage this account."},
                status=403,
            )

        deactivating = request.data.get("is_active") in (False, "false", "False", 0, "0")

        if deactivating and leaves_no_active_super_admin(user):
            return Response(
                {"error": "The last active super admin cannot be deactivated."},
                status=403,
            )

        serializer = UserSerializer(
            user,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user = get_object_or_404(User, id=pk)

        if user.pk == request.user.pk:
            return Response(
                {"error": "You may not delete your own account."},
                status=403,
            )

        if not can_administer(request.user, user):
            return Response(
                {"error": "You may not manage this account."},
                status=403,
            )

        if leaves_no_active_super_admin(user):
            return Response(
                {"error": "The last active super admin cannot be deleted."},
                status=403,
            )

        user.delete()
        return Response({"success": True}, status=200)
