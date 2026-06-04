import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User


class InternshipType(models.TextChoices):
    REMOTE = "remote", "Remote"
    ON_SITE = "on_site", "On-Site"
    HYBRID = "hybrid", "Hybrid"


class InternshipStatus(models.TextChoices):
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"
    DRAFT = "draft", "Draft"


class Internship(models.Model):
    """
    An internship posting created by a company user.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="internships",
        limit_choices_to={"role": "company"},
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    internship_type = models.CharField(
        max_length=20,
        choices=InternshipType.choices,
        default=InternshipType.REMOTE,
    )
    status = models.CharField(
        max_length=20,
        choices=InternshipStatus.choices,
        default=InternshipStatus.OPEN,
        db_index=True,
    )
    stipend_per_month = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    duration_months = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(24)],
        help_text="Duration in months",
    )
    openings = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    application_deadline = models.DateField(null=True, blank=True, db_index=True)
    skills_required = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "internships"
        verbose_name = "Internship"
        verbose_name_plural = "Internships"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["company", "status"]),
        ]

    def __str__(self):
        return f"{self.title} @ {self.company.company_name}"
