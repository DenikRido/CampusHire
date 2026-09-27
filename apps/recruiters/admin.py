from django.contrib import admin

from .models import RecruiterProfile


@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "designation", "phone")
    search_fields = ("user__email", "designation")
    readonly_fields = ("created_at", "updated_at")
