from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.accounts.models import UserRole


class IsCompanyOrReadOnly(BasePermission):
    """
    Allow read access to everyone authenticated.
    Write access only to company-role users who own the resource.
    """

    message = "Only company accounts can create or modify internships."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_company

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.company == request.user
