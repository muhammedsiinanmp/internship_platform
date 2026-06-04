from django.contrib import admin
from .models import Internship


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "status", "internship_type", "duration_months", "created_at")
    list_filter = ("status", "internship_type")
    search_fields = ("title", "company__email", "company__company_name", "location")
    ordering = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("company",)
