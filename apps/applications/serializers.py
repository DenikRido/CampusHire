from __future__ import annotations

from rest_framework import serializers

from apps.jobs.serializers import JobSerializer

from .models import Application, ApplicationStatusHistory


class ApplicationStatusHistorySerializer(serializers.ModelSerializer):
    changed_by_email = serializers.EmailField(source="changed_by.email", read_only=True)

    class Meta:
        model = ApplicationStatusHistory
        fields = ("id", "old_status", "new_status", "changed_by_email", "changed_at", "remarks")


class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    job_id = serializers.IntegerField(write_only=True)
    student_name = serializers.CharField(source="student.user.full_name", read_only=True)
    student_email = serializers.EmailField(source="student.user.email", read_only=True)
    registration_number = serializers.CharField(source="student.registration_number", read_only=True)
    department = serializers.CharField(source="student.department", read_only=True)
    cgpa = serializers.DecimalField(source="student.cgpa", max_digits=4, decimal_places=2, read_only=True)
    resume_url = serializers.SerializerMethodField()
    history = ApplicationStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "job",
            "job_id",
            "student_name",
            "student_email",
            "registration_number",
            "department",
            "cgpa",
            "cover_letter",
            "status",
            "applied_at",
            "updated_at",
            "resume_url",
            "history",
        )
        read_only_fields = ("id", "status", "applied_at", "updated_at")

    def get_resume_url(self, obj):
        file = obj.resume_snapshot or obj.student.resume
        if not file:
            return ""
        request = self.context.get("request")
        return request.build_absolute_uri(file.url) if request else file.url


class ApplicationStatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField()
    remarks = serializers.CharField(required=False, allow_blank=True)
