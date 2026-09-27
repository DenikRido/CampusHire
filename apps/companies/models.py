from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.constants import CompanyVerificationStatus


class Company(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="companies",
        limit_choices_to={"role": "RECRUITER"},
    )
    company_name = models.CharField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=80, blank=True)
    location = models.CharField(max_length=120, blank=True, db_index=True)
    verification_status = models.CharField(
        max_length=20,
        choices=CompanyVerificationStatus.choices,
        default=CompanyVerificationStatus.PENDING,
        db_index=True,
    )
    verification_notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["verification_status", "location"]),
        ]
        ordering = ["company_name"]
        verbose_name_plural = "companies"

    def __str__(self) -> str:
        return self.company_name

    @property
    def is_verified(self) -> bool:
        return self.verification_status == CompanyVerificationStatus.VERIFIED
