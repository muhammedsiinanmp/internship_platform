import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager


class UserRole(models.TextChoices):
    STUDENT = "student", "Student"
    COMPANY = "company", "Company"
    ADMIN = "admin", "Admin"


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as the unique identifier.
    Supports STUDENT and COMPANY roles.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        db_index=True,
    )

    # Company-specific fields
    company_name = models.CharField(max_length=255, blank=True)
    company_website = models.URLField(blank=True)

    # Student-specific fields
    university = models.CharField(max_length=255, blank=True)
    graduation_year = models.PositiveSmallIntegerField(null=True, blank=True)
    resume_url = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "role"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["email", "role"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} <{self.email}>"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_student(self):
        return self.role == UserRole.STUDENT

    @property
    def is_company(self):
        return self.role == UserRole.COMPANY
