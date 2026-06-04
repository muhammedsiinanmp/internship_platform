from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "first_name", "last_name", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name", "company_name")
    ordering = ("-date_joined",)
    readonly_fields = ("id", "date_joined", "updated_at")

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "role")}),
        ("Company Info", {"fields": ("company_name", "company_website")}),
        ("Student Info", {"fields": ("university", "graduation_year", "resume_url")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("date_joined", "updated_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2"),
        }),
    )