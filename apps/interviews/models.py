from __future__ import annotations

from django.db import models

from apps.applications.models import Application
from apps.common.constants import InterviewMode, InterviewResult


class Interview(models.Model):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="interviews",
    )
    scheduled_at = models.DateTimeField(db_index=True)
    mode = models.CharField(max_length=16, choices=InterviewMode.choices, default=InterviewMode.ONLINE)
    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=160, blank=True)
    interviewer_name = models.CharField(max_length=120)
    notes = models.TextField(blank=True)
    result = models.CharField(
        max_length=16,
        choices=InterviewResult.choices,
        default=InterviewResult.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_at"]
        indexes = [
            models.Index(fields=["scheduled_at", "result"]),
        ]

    def __str__(self) -> str:
        return f"Interview #{self.pk} for application {self.application_id}"
