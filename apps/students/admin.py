from django.contrib import admin

from .models import Education, Skill, StudentProfile, StudentSkill


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class StudentSkillInline(admin.TabularInline):
    model = StudentSkill
    extra = 0


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "registration_number",
        "user",
        "department",
        "degree",
        "graduation_year",
        "cgpa",
        "backlogs",
    )
    list_filter = ("department", "degree", "graduation_year")
    search_fields = ("registration_number", "user__email", "user__first_name")
    inlines = [EducationInline, StudentSkillInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name",)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("student", "institution", "degree", "start_year", "end_year")
    search_fields = ("institution", "student__registration_number")
