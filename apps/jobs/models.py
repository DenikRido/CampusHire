from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from apps.common.constants import EmploymentType, JobStatus
from apps.companies.models import Company
from apps.students.models import Skill


class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=160, db_index=True)
    description = models.TextField()
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
        db_index=True,
    )
    location = models.CharField(max_length=120, db_index=True)
    minimum_cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    maximum_backlogs = models.PositiveIntegerField(default=10)
    eligible_departments = models.JSONField(default=list, blank=True)
    eligible_degrees = models.JSONField(default=list, blank=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    required_skills = models.ManyToManyField(Skill, related_name="jobs", blank=True)
    application_deadline = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=24,
        choices=JobStatus.choices,
        default=JobStatus.DRAFT,
        db_index=True,
    )
    rejection_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "application_deadline"]),
            models.Index(fields=["status", "location"]),
            models.Index(fields=["title"]),
            models.Index(fields=["employment_type", "status"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} @ {self.company.company_name}"

    @property
    def salary_range(self) -> str:
        if self.salary_min and self.salary_max:
            return f"₹{self.salary_min:,} – ₹{self.salary_max:,}"
        if self.salary_min:
            return f"₹{self.salary_min:,}+"
        if self.salary_max:
            return f"Up to ₹{self.salary_max:,}"
        return "Not disclosed"

    @property
    def is_open_for_applications(self) -> bool:
        return (
            self.status == JobStatus.ACTIVE
            and self.application_deadline >= timezone.now()
        )
