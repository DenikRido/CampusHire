from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator
from django.db import models

from apps.common.constants import Degree, Department, Gender, SkillProficiency
from apps.common.utils import resume_upload_to
from apps.common.validators import validate_resume_file


class StudentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    registration_number = models.CharField(max_length=40, unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=32, choices=Gender.choices, blank=True)
    department = models.CharField(max_length=16, choices=Department.choices, db_index=True)
    degree = models.CharField(max_length=16, choices=Degree.choices)
    graduation_year = models.PositiveIntegerField(db_index=True)
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("10"))],
    )
    backlogs = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0)])
    github_url = models.URLField(blank=True, validators=[URLValidator()])
    linkedin_url = models.URLField(blank=True, validators=[URLValidator()])
    portfolio_url = models.URLField(blank=True, validators=[URLValidator()])
    resume = models.FileField(
        upload_to=resume_upload_to,
        blank=True,
        null=True,
        validators=[validate_resume_file],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["department", "graduation_year"]),
            models.Index(fields=["cgpa"]),
        ]
        ordering = ["registration_number"]

    def __str__(self) -> str:
        return f"{self.registration_number} ({self.user.email})"

    @property
    def has_resume(self) -> bool:
        return bool(self.resume)


class Education(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=160)
    degree = models.CharField(max_length=80)
    field_of_study = models.CharField(max_length=120, blank=True)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)
    score = models.CharField(max_length=40, blank=True)

    class Meta:
        ordering = ["-end_year", "-start_year"]

    def __str__(self) -> str:
        return f"{self.degree} @ {self.institution}"


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        super().save(*args, **kwargs)


class StudentSkill(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="student_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="student_links")
    proficiency = models.CharField(
        max_length=20,
        choices=SkillProficiency.choices,
        default=SkillProficiency.INTERMEDIATE,
    )

    class Meta:
        unique_together = ("student", "skill")
        ordering = ["skill__name"]

    def __str__(self) -> str:
        return f"{self.student.registration_number} – {self.skill.name}"
