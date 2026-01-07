from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return getattr(request.user, "role", None) == "SUPER_ADMIN"

class IsPasswordChanged(BasePermission):
    """
    Allow access only after first password change
    """
    def has_permission(self, request, view):
        return not getattr(request.user, "is_first_login", True)