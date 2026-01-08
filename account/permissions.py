from rest_framework.permissions import BasePermission
from onboarding.models import Onboarding


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return getattr(request.user, "role", None) == "SUPER_ADMIN"
    

class IsOnboardingApproved(BasePermission):
    message = "Complete onboarding and get approval to access the system."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Admin bypass
        if user.role == "SUPER_ADMIN":
            return True

        # Force password change
        if user.is_first_login:
            return False

        onboarding = Onboarding.objects.filter(employee=user).first()
        if not onboarding:
            return False

        return onboarding.status == "APPROVED"