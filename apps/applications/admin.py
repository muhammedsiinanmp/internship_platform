from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("student", "internship", "status", "applied_at")
    list_filter = ("status",)
    search_fields = ("student__email", "internship__title")
    ordering = ("-applied_at",)
    readonly_fields = ("id", "applied_at", "updated_at")
    raw_id_fields = ("student", "internship")
