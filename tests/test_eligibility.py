from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.jobs.services import check_student_eligibility
from apps.students.models import StudentProfile

pytestmark = pytest.mark.django_db


def test_valid_student_is_eligible(student_user, active_job):
    result = check_student_eligibility(student_user.student_profile, active_job)
    assert result.eligible is True
    assert result.reasons == []


def test_low_cgpa(student_user, active_job):
    profile = student_user.student_profile
    profile.cgpa = Decimal("6.00")
    profile.save()
    result = check_student_eligibility(profile, active_job)
    assert result.eligible is False
    assert any("CGPA" in r for r in result.reasons)


def test_too_many_backlogs(student_user, active_job):
    profile = student_user.student_profile
    profile.backlogs = 5
    profile.save()
    result = check_student_eligibility(profile, active_job)
    assert result.eligible is False
    assert any("backlog" in r.lower() for r in result.reasons)


def test_wrong_department(weak_student, active_job):
    result = check_student_eligibility(weak_student.student_profile, active_job)
    assert result.eligible is False
    assert any("department" in r.lower() for r in result.reasons)


def test_wrong_graduation_year(student_user, active_job):
    profile = student_user.student_profile
    profile.graduation_year = 2024
    profile.save()
    result = check_student_eligibility(profile, active_job)
    assert result.eligible is False
    assert any("graduation year" in r.lower() for r in result.reasons)


def test_missing_resume(student_user, active_job):
    profile = student_user.student_profile
    profile.resume = None
    profile.save()
    result = check_student_eligibility(profile, active_job)
    assert result.eligible is False
    assert any("resume" in r.lower() for r in result.reasons)


def test_missing_required_skill(student_user, active_job):
    profile = student_user.student_profile
    profile.student_skills.all().delete()
    result = check_student_eligibility(profile, active_job)
    assert result.eligible is False
    assert any("Python" in r for r in result.reasons)


def test_expired_job(student_user, active_job):
    active_job.application_deadline = timezone.now() - timedelta(hours=1)
    active_job.save()
    result = check_student_eligibility(student_user.student_profile, active_job)
    assert result.eligible is False
    assert any("deadline" in r.lower() for r in result.reasons)


def test_eligibility_api(api_client, student_user, active_job):
    api_client.force_authenticate(student_user)
    resp = api_client.get(f"/api/jobs/{active_job.id}/eligibility/")
    assert resp.status_code == 200
    assert resp.data["eligible"] is True
