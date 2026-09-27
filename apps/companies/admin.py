from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("company_name", "owner", "industry", "location", "verification_status")
    list_filter = ("verification_status", "industry", "location")
    search_fields = ("company_name", "owner__email", "industry")
    readonly_fields = ("created_at", "updated_at")
