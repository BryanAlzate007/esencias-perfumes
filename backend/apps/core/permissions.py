from rest_framework.permissions import BasePermission


def user_role(user):
    profile = getattr(user, "profile", None)
    if profile:
        return profile.role
    return "customer"


def is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_staff or user_role(user) == "admin"))


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return is_admin_user(request.user)
