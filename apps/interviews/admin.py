from django.contrib import admin

from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "scheduled_at", "mode", "interviewer_name", "result")
    list_filter = ("mode", "result")
    search_fields = ("interviewer_name", "application__student__user__email")
    readonly_fields = ("created_at", "updated_at")
