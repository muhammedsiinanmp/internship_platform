import uuid
from django.db import models
from apps.accounts.models import User
from apps.internships.models import Internship


class ApplicationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    REVIEWED = "reviewed", "Reviewed"
    SHORTLISTED = "shortlisted", "Shortlisted"
    REJECTED = "rejected", "Rejected"
    ACCEPTED = "accepted", "Accepted"


class Application(models.Model):
    """
    A student's application to an internship.
    UNIQUE constraint prevents double-applying.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications",
        limit_choices_to={"role": "student"},
    )
    internship = models.ForeignKey(
        Internship,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
        db_index=True,
    )
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "applications"
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        ordering = ["-applied_at"]
        # ⭐ Core constraint: prevents a student from applying twice
        constraints = [
            models.UniqueConstraint(
                fields=["student", "internship"],
                name="unique_student_internship_application",
            )
        ]
        indexes = [
            models.Index(fields=["student", "status"]),
            models.Index(fields=["internship", "status"]),
        ]

    def __str__(self):
        return f"{self.student.email} → {self.internship.title}"
