from django.contrib import admin

from .models import Application, ApplicationStatusHistory


class HistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ("old_status", "new_status", "changed_by", "changed_at", "remarks")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "job", "status", "applied_at")
    list_filter = ("status",)
    search_fields = ("student__registration_number", "student__user__email", "job__title")
    readonly_fields = ("applied_at", "updated_at")
    inlines = [HistoryInline]


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("application", "old_status", "new_status", "changed_by", "changed_at")
    list_filter = ("new_status",)
    readonly_fields = ("changed_at",)
