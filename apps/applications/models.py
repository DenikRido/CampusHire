from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.constants import ApplicationStatus
from apps.jobs.models import Job
from apps.students.models import StudentProfile


class Application(models.Model):
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    resume_snapshot = models.FileField(upload_to="applications/resumes/", blank=True, null=True)
    cover_letter = models.TextField(blank=True)
    status = models.CharField(
        max_length=32,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.APPLIED,
        db_index=True,
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "job"], name="uniq_student_job_application"),
        ]
        indexes = [
            models.Index(fields=["status", "applied_at"]),
            models.Index(fields=["job", "status"]),
        ]
        ordering = ["-applied_at"]

    def __str__(self) -> str:
        return f"{self.student.registration_number} → {self.job.title} [{self.status}]"


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="history",
    )
    old_status = models.CharField(max_length=32, choices=ApplicationStatus.choices, blank=True)
    new_status = models.CharField(max_length=32, choices=ApplicationStatus.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="application_status_changes",
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-changed_at"]
        verbose_name_plural = "application status histories"

    def __str__(self) -> str:
        return f"{self.application_id}: {self.old_status} → {self.new_status}"
