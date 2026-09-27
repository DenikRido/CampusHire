from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.applications.models import Application
from apps.applications.services import apply_to_job, change_application_status
from apps.common.constants import ApplicationStatus
from tests.conftest import auth

pytestmark = pytest.mark.django_db


@pytest.fixture
def shortlisted_application(student_user, active_job, recruiter_user):
    application = apply_to_job(student=student_user.student_profile, job=active_job)
    change_application_status(application=application, new_status=ApplicationStatus.UNDER_REVIEW, actor=recruiter_user)
    application.refresh_from_db()
    change_application_status(application=application, new_status=ApplicationStatus.SHORTLISTED, actor=recruiter_user)
    application.refresh_from_db()
    return application


def test_create_interview(api_client, recruiter_user, shortlisted_application):
    auth(api_client, recruiter_user)
    when = (timezone.now() + timedelta(days=2)).isoformat()
    resp = api_client.post(
        "/api/interviews/",
        {
            "application_id": shortlisted_application.id,
            "scheduled_at": when,
            "mode": "ONLINE",
            "meeting_link": "https://meet.example.com/abc",
            "interviewer_name": "Kavya Rao",
        },
        format="json",
    )
    assert resp.status_code == 201
    shortlisted_application.refresh_from_db()
    assert shortlisted_application.status == ApplicationStatus.INTERVIEW_SCHEDULED


def test_student_cannot_create_interview(api_client, student_user, shortlisted_application):
    auth(api_client, student_user)
    resp = api_client.post(
        "/api/interviews/",
        {
            "application_id": shortlisted_application.id,
            "scheduled_at": (timezone.now() + timedelta(days=1)).isoformat(),
            "mode": "ONLINE",
            "meeting_link": "https://meet.example.com/x",
            "interviewer_name": "X",
        },
        format="json",
    )
    assert resp.status_code == 403


def test_past_interview_rejected(api_client, recruiter_user, shortlisted_application):
    auth(api_client, recruiter_user)
    resp = api_client.post(
        "/api/interviews/",
        {
            "application_id": shortlisted_application.id,
            "scheduled_at": (timezone.now() - timedelta(days=1)).isoformat(),
            "mode": "ONLINE",
            "meeting_link": "https://meet.example.com/x",
            "interviewer_name": "X",
        },
        format="json",
    )
    assert resp.status_code == 400
