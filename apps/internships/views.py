import logging
from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from core.mixins import SuccessResponseMixin
from .models import Internship, InternshipStatus
from .serializers import InternshipSerializer
from .permissions import IsCompanyOrReadOnly
from .filters import InternshipFilter

logger = logging.getLogger(__name__)


@extend_schema(tags=["Internships"])
class InternshipListCreateView(SuccessResponseMixin, generics.ListCreateAPIView):
    """
    GET  — List all open internships (all authenticated users).
    POST — Create a new internship (company only).
    """

    serializer_class = InternshipSerializer
    permission_classes = [IsCompanyOrReadOnly]
    filterset_class = InternshipFilter
    search_fields = ["title", "description", "location", "company__company_name"]
    ordering_fields = ["created_at", "stipend_per_month", "duration_months", "application_deadline"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        # Companies see their own; students see only open
        if user.is_company:
            return Internship.objects.filter(company=user).select_related("company")
        return (
            Internship.objects.filter(status=InternshipStatus.OPEN)
            .select_related("company")
            .prefetch_related("applications")
        )

    def perform_create(self, serializer):
        serializer.save(company=self.request.user)
        logger.info("Internship created by company %s", self.request.user.email)


@extend_schema(tags=["Internships"])
class InternshipRetrieveUpdateDestroyView(SuccessResponseMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    GET    — Retrieve a single internship.
    PATCH  — Update (company owner only).
    DELETE — Delete (company owner only).
    """

    serializer_class = InternshipSerializer
    permission_classes = [IsCompanyOrReadOnly]
    lookup_field = "pk"

    def get_queryset(self):
        return Internship.objects.select_related("company").prefetch_related("applications")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"status": "success", "message": "Internship deleted successfully."},
            status=status.HTTP_200_OK,
        )
