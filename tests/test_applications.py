from __future__ import annotations

import pytest
from rest_framework import status

from apps.applications.models import Application, ApplicationStatusHistory
from apps.common.constants import ApplicationStatus
from tests.conftest import auth

pytestmark = pytest.mark.django_db


def test_successful_application(api_client, student_user, active_job):
    auth(api_client, student_user)
    resp = api_client.post(
        "/api/applications/",
        {"job_id": active_job.id, "cover_letter": "Please consider me."},
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    app = Application.objects.get(pk=resp.data["id"])
    assert app.status == ApplicationStatus.APPLIED
    assert ApplicationStatusHistory.objects.filter(application=app).exists()


def test_duplicate_application_rejected(api_client, student_user, active_job):
    auth(api_client, student_user)
    api_client.post("/api/applications/", {"job_id": active_job.id}, format="json")
    resp = api_client.post("/api/applications/", {"job_id": active_job.id}, format="json")
    assert resp.status_code in (400, 409)


def test_expired_job_application_rejected(api_client, student_user, active_job):
    from datetime import timedelta

    from django.utils import timezone

    active_job.application_deadline = timezone.now() - timedelta(days=1)
    active_job.save()
    auth(api_client, student_user)
    resp = api_client.post("/api/applications/", {"job_id": active_job.id}, format="json")
    assert resp.status_code == 400
    assert resp.data.get("eligible") is False


def test_status_transition_and_history(api_client, student_user, recruiter_user, active_job):
    auth(api_client, student_user)
    created = api_client.post("/api/applications/", {"job_id": active_job.id}, format="json")
    app_id = created.data["id"]
    auth(api_client, recruiter_user)
    resp = api_client.patch(
        f"/api/applications/{app_id}/status/",
        {"status": "UNDER_REVIEW", "remarks": "Screening"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.data["status"] == "UNDER_REVIEW"
    assert ApplicationStatusHistory.objects.filter(application_id=app_id, new_status="UNDER_REVIEW").exists()


def test_invalid_status_transition(api_client, student_user, recruiter_user, active_job):
    auth(api_client, student_user)
    created = api_client.post("/api/applications/", {"job_id": active_job.id}, format="json")
    auth(api_client, recruiter_user)
    resp = api_client.patch(
        f"/api/applications/{created.data['id']}/status/",
        {"status": "SELECTED"},
        format="json",
    )
    assert resp.status_code == 400


def test_other_recruiter_cannot_update_status(api_client, student_user, other_recruiter, active_job):
    auth(api_client, student_user)
    created = api_client.post("/api/applications/", {"job_id": active_job.id}, format="json")
    auth(api_client, other_recruiter)
    resp = api_client.patch(
        f"/api/applications/{created.data['id']}/status/",
        {"status": "UNDER_REVIEW"},
        format="json",
    )
    assert resp.status_code in (403, 404)


def test_withdraw(api_client, student_user, active_job):
    auth(api_client, student_user)
    created = api_client.post("/api/applications/", {"job_id": active_job.id}, format="json")
    resp = api_client.post(f"/api/applications/{created.data['id']}/withdraw/", {}, format="json")
    assert resp.status_code == 200
    assert resp.data["status"] == "WITHDRAWN"
