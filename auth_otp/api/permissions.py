# permissions.py
from rest_framework.permissions import BasePermission


class IsAuthenticatedAndStaff(BasePermission):
    """
    Allows access only to authenticated staff users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )
