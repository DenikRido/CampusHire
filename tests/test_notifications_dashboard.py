from __future__ import annotations

import pytest

from apps.applications.services import apply_to_job
from apps.notifications.models import Notification
from tests.conftest import auth

pytestmark = pytest.mark.django_db


def test_application_creates_notifications(student_user, active_job, recruiter_user):
    apply_to_job(student=student_user.student_profile, job=active_job, cover_letter="Hi")
    assert Notification.objects.filter(recipient=student_user, title="Application submitted").exists()
    assert Notification.objects.filter(recipient=recruiter_user, title="New application received").exists()


def test_mark_notification_read(api_client, student_user, active_job):
    apply_to_job(student=student_user.student_profile, job=active_job)
    note = Notification.objects.filter(recipient=student_user).first()
    auth(api_client, student_user)
    resp = api_client.patch(f"/api/notifications/{note.id}/read/", {}, format="json")
    assert resp.status_code == 200
    note.refresh_from_db()
    assert note.is_read is True


def test_student_cannot_read_others_notifications(api_client, student_user, recruiter_user, active_job):
    apply_to_job(student=student_user.student_profile, job=active_job)
    note = Notification.objects.filter(recipient=recruiter_user).first()
    auth(api_client, student_user)
    resp = api_client.patch(f"/api/notifications/{note.id}/read/", {}, format="json")
    assert resp.status_code == 404


def test_student_dashboard(api_client, student_user, active_job):
    apply_to_job(student=student_user.student_profile, job=active_job)
    auth(api_client, student_user)
    resp = api_client.get("/api/dashboard/student/")
    assert resp.status_code == 200
    assert resp.data["total_applications"] >= 1
    assert resp.data["available_jobs"] >= 1


def test_recruiter_dashboard(api_client, recruiter_user):
    auth(api_client, recruiter_user)
    resp = api_client.get("/api/dashboard/recruiter/")
    assert resp.status_code == 200
    assert "active_jobs" in resp.data


def test_admin_dashboard(api_client, admin_user, student_user, recruiter_user):
    auth(api_client, admin_user)
    resp = api_client.get("/api/dashboard/admin/")
    assert resp.status_code == 200
    assert resp.data["total_students"] >= 1
    assert resp.data["total_recruiters"] >= 1


def test_student_cannot_access_admin_dashboard(api_client, student_user):
    auth(api_client, student_user)
    resp = api_client.get("/api/dashboard/admin/")
    assert resp.status_code == 403
