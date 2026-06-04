from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.accounts.models import UserRole


class IsStudentOrCompanyReadOnly(BasePermission):
    """
    Students can apply and view their own applications.
    Companies can view applications for their internships.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Student sees own application
        if user.is_student:
            return obj.student == user
        # Company sees applications for their internships
        if user.is_company:
            return obj.internship.company == user
        return False
