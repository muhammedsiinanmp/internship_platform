import logging
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import SuccessResponseMixin
from .models import Application
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationListSerializer,
    ApplicationStatusUpdateSerializer,
)
from .permissions import IsStudentOrCompanyReadOnly

logger = logging.getLogger(__name__)


@extend_schema(tags=["Applications"])
class ApplicationCreateView(SuccessResponseMixin, generics.CreateAPIView):
    """
    POST — Student applies to an internship.
    """

    serializer_class = ApplicationCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Only students can apply
        perms = super().get_permissions()
        return perms

    def create(self, request, *args, **kwargs):
        if not request.user.is_student:
            return Response(
                {"status": "error", "errors": {"detail": "Only students can apply for internships."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save(student=request.user)
        logger.info(
            "Application submitted: student=%s internship=%s",
            request.user.email,
            application.internship_id,
        )
        return self.success_response(
            data=ApplicationListSerializer(application).data,
            message="Application submitted successfully.",
            http_status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Applications"])
class ApplicationListView(SuccessResponseMixin, generics.ListAPIView):
    """
    GET — List applications.
    Students see their own applications.
    Companies see applications for their internships.
    """

    serializer_class = ApplicationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["internship__title", "student__email", "student__first_name"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ["applied_at", "status"]
    ordering = ["-applied_at"]

    def get_queryset(self):
        user = self.request.user
        qs = Application.objects.select_related(
            "student", "internship", "internship__company"
        )
        if user.is_student:
            return qs.filter(student=user)
        if user.is_company:
            # Allow filtering by internship_id
            internship_id = self.request.query_params.get("internship_id")
            company_qs = qs.filter(internship__company=user)
            if internship_id:
                company_qs = company_qs.filter(internship__id=internship_id)
            return company_qs
        return Application.objects.none()


@extend_schema(tags=["Applications"])
class ApplicationDetailView(SuccessResponseMixin, generics.RetrieveUpdateAPIView):
    """
    GET   — Retrieve a single application.
    PATCH — Company updates the application status.
    """

    permission_classes = [IsStudentOrCompanyReadOnly]
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method in ("PATCH", "PUT"):
            return ApplicationStatusUpdateSerializer
        return ApplicationListSerializer

    def get_queryset(self):
        return Application.objects.select_related(
            "student", "internship", "internship__company"
        )

    def update(self, request, *args, **kwargs):
        if not request.user.is_company:
            return Response(
                {"status": "error", "errors": {"detail": "Only companies can update application status."}},
                status=status.HTTP_403_FORBIDDEN,
            )
        kwargs["partial"] = True
        return super().update(request, *args, **kwargs)
