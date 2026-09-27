from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from rest_framework.test import APIClient

from apps.common.constants import (
    CompanyVerificationStatus,
    Degree,
    Department,
    EmploymentType,
    JobStatus,
    Role,
)
from apps.companies.models import Company
from apps.jobs.models import Job
from apps.recruiters.models import RecruiterProfile
from apps.students.models import Skill, StudentProfile, StudentSkill
from django.contrib.auth import get_user_model

User = get_user_model()

MINI_PDF = b"%PDF-1.1\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def password():
    return "CampusHire@123"


def _user(email, role, password, **kwargs):
    return User.objects.create_user(
        email=email,
        password=password,
        first_name=kwargs.get("first_name", "Test"),
        last_name=kwargs.get("last_name", "User"),
        role=role,
        is_staff=role == Role.ADMIN,
        is_superuser=role == Role.ADMIN,
    )


@pytest.fixture
def admin_user(password):
    return _user("admin@test.local", Role.ADMIN, password, first_name="Admin")


@pytest.fixture
def student_user(password):
    user = _user("student@test.local", Role.STUDENT, password, first_name="Priya")
    profile = StudentProfile.objects.create(
        user=user,
        registration_number="CSE0001",
        department=Department.CSE,
        degree=Degree.BTECH,
        graduation_year=2026,
        cgpa=Decimal("8.50"),
        backlogs=0,
        resume=SimpleUploadedFile("resume.pdf", MINI_PDF, content_type="application/pdf"),
    )
    python, _ = Skill.objects.get_or_create(name="Python")
    django, _ = Skill.objects.get_or_create(name="Django")
    StudentSkill.objects.create(student=profile, skill=python)
    StudentSkill.objects.create(student=profile, skill=django)
    return user


@pytest.fixture
def weak_student(password):
    user = _user("weak@test.local", Role.STUDENT, password, first_name="Weak")
    StudentProfile.objects.create(
        user=user,
        registration_number="MECH0002",
        department=Department.MECH,
        degree=Degree.BE,
        graduation_year=2024,
        cgpa=Decimal("5.00"),
        backlogs=4,
    )
    return user


@pytest.fixture
def recruiter_user(password):
    user = _user("recruiter@test.local", Role.RECRUITER, password, first_name="Kavya")
    RecruiterProfile.objects.create(user=user, designation="Campus Lead")
    Company.objects.create(
        owner=user,
        company_name="Nimbus Labs",
        industry="Software",
        location="Bengaluru",
        verification_status=CompanyVerificationStatus.VERIFIED,
    )
    return user


@pytest.fixture
def other_recruiter(password):
    user = _user("other.rec@test.local", Role.RECRUITER, password, first_name="Other")
    RecruiterProfile.objects.create(user=user)
    Company.objects.create(
        owner=user,
        company_name="Helix Finance",
        verification_status=CompanyVerificationStatus.VERIFIED,
        location="Mumbai",
    )
    return user


@pytest.fixture
def active_job(recruiter_user):
    company = recruiter_user.companies.first()
    python = Skill.objects.get_or_create(name="Python")[0]
    job = Job.objects.create(
        company=company,
        title="Backend Engineer",
        description="Django APIs",
        employment_type=EmploymentType.FULL_TIME,
        location="Bengaluru",
        minimum_cgpa=Decimal("7.00"),
        maximum_backlogs=1,
        eligible_departments=[Department.CSE, Department.IT],
        eligible_degrees=[Degree.BTECH],
        graduation_year=2026,
        salary_min=800000,
        salary_max=1200000,
        application_deadline=timezone.now() + timedelta(days=10),
        status=JobStatus.ACTIVE,
    )
    job.required_skills.add(python)
    return job


def auth(client, user):
    client.force_authenticate(user=user)
    return client
