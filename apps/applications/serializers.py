from django.db import IntegrityError
from rest_framework import serializers
from .models import Application, ApplicationStatus
from apps.internships.models import Internship, InternshipStatus


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["id", "internship", "cover_letter", "status", "applied_at"]
        read_only_fields = ["id", "status", "applied_at"]

    def validate_internship(self, internship):
        if internship.status != InternshipStatus.OPEN:
            raise serializers.ValidationError("This internship is not accepting applications.")
        return internship

    def validate(self, attrs):
        student = self.context["request"].user
        internship = attrs.get("internship")
        if Application.objects.filter(student=student, internship=internship).exists():
            raise serializers.ValidationError(
                {"internship": "You have already applied to this internship."}
            )
        return attrs

    def create(self, validated_data):
        try:
            return Application.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {"internship": "You have already applied to this internship."}
            )


class ApplicationListSerializer(serializers.ModelSerializer):
    internship_title = serializers.CharField(source="internship.title", read_only=True)
    internship_id = serializers.UUIDField(source="internship.id", read_only=True)
    company_name = serializers.CharField(source="internship.company.company_name", read_only=True)
    student_name = serializers.SerializerMethodField(read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "internship_id",
            "internship_title",
            "company_name",
            "student_name",
            "student_email",
            "status",
            "cover_letter",
            "applied_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_student_name(self, obj):
        return obj.student.get_full_name()


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    """Used by company to update application status."""

    class Meta:
        model = Application
        fields = ["id", "status", "updated_at"]
        read_only_fields = ["id", "updated_at"]

    def validate_status(self, value):
        allowed = [
            ApplicationStatus.REVIEWED,
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.ACCEPTED,
        ]
        if value not in allowed:
            raise serializers.ValidationError(f"Status must be one of: {allowed}")
        return value
