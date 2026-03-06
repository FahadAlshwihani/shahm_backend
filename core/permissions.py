from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role == "super_admin"


class IsAdminOrSuper(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role in ["admin", "super_admin"]


class IsEditorOrAbove(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role in ["editor", "admin", "super_admin"]
