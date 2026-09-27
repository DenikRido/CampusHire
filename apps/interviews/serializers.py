from __future__ import annotations

from rest_framework import serializers

from .models import Interview


class InterviewSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="application.job.title", read_only=True)
    student_name = serializers.CharField(source="application.student.user.full_name", read_only=True)
    application_id = serializers.IntegerField()

    class Meta:
        model = Interview
        fields = (
            "id",
            "application_id",
            "job_title",
            "student_name",
            "scheduled_at",
            "mode",
            "meeting_link",
            "location",
            "interviewer_name",
            "notes",
            "result",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "job_title", "student_name", "created_at", "updated_at")
