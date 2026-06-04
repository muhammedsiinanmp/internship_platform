from rest_framework import serializers
from .models import Internship
from apps.accounts.serializers import UserProfileSerializer


class InternshipSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.company_name", read_only=True)
    company_id = serializers.UUIDField(source="company.id", read_only=True)
    application_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Internship
        fields = [
            "id",
            "company_id",
            "company_name",
            "title",
            "description",
            "requirements",
            "location",
            "internship_type",
            "status",
            "stipend_per_month",
            "duration_months",
            "openings",
            "application_deadline",
            "skills_required",
            "application_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "company_id", "company_name", "created_at", "updated_at"]

    def get_application_count(self, obj):
        return obj.applications.count()

    def validate_skills_required(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("skills_required must be a list of strings.")
        return [str(skill).strip() for skill in value if str(skill).strip()]
