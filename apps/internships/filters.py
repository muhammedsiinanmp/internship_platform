import django_filters
from .models import Internship, InternshipType, InternshipStatus


class InternshipFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    location = django_filters.CharFilter(lookup_expr="icontains")
    internship_type = django_filters.ChoiceFilter(choices=InternshipType.choices)
    status = django_filters.ChoiceFilter(choices=InternshipStatus.choices)
    stipend_min = django_filters.NumberFilter(field_name="stipend_per_month", lookup_expr="gte")
    stipend_max = django_filters.NumberFilter(field_name="stipend_per_month", lookup_expr="lte")
    duration_min = django_filters.NumberFilter(field_name="duration_months", lookup_expr="gte")
    deadline_before = django_filters.DateFilter(field_name="application_deadline", lookup_expr="lte")
    company = django_filters.UUIDFilter(field_name="company__id")

    class Meta:
        model = Internship
        fields = ["title", "location", "internship_type", "status", "company"]
