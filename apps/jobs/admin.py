from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "location",
        "employment_type",
        "status",
        "application_deadline",
    )
    list_filter = ("status", "employment_type", "location", "graduation_year")
    search_fields = ("title", "company__company_name", "location", "description")
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("required_skills",)
    date_hierarchy = "application_deadline"
