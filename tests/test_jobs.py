from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from apps.common.constants import JobStatus
from apps.jobs.models import Job
from tests.conftest import auth

pytestmark = pytest.mark.django_db


def test_recruiter_creates_job(api_client, recruiter_user):
    auth(api_client, recruiter_user)
    deadline = (timezone.now() + timedelta(days=7)).isoformat()
    resp = api_client.post(
        "/api/jobs/",
        {
            "title": "QA Intern",
            "description": "Test Django APIs",
            "employment_type": "INTERNSHIP",
            "location": "Chennai",
            "minimum_cgpa": "7.0",
            "maximum_backlogs": 1,
            "eligible_departments": ["CSE"],
            "eligible_degrees": ["BTECH"],
            "application_deadline": deadline,
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    job = Job.objects.get(pk=resp.data["id"])
    assert job.status == JobStatus.DRAFT
    assert job.company.owner == recruiter_user


def test_student_cannot_create_job(api_client, student_user):
    auth(api_client, student_user)
    resp = api_client.post("/api/jobs/", {"title": "Nope"}, format="json")
    assert resp.status_code == 403


def test_admin_approves_job(api_client, recruiter_user, admin_user):
    auth(api_client, recruiter_user)
    deadline = (timezone.now() + timedelta(days=7)).isoformat()
    created = api_client.post(
        "/api/jobs/",
        {
            "title": "Platform Engineer",
            "description": "Infra",
            "employment_type": "FULL_TIME",
            "location": "Pune",
            "minimum_cgpa": "8.0",
            "maximum_backlogs": 0,
            "application_deadline": deadline,
        },
        format="json",
    )
    job_id = created.data["id"]
    api_client.post(f"/api/jobs/{job_id}/submit/", {}, format="json")
    auth(api_client, admin_user)
    resp = api_client.post(f"/api/jobs/{job_id}/approve/", {}, format="json")
    assert resp.status_code == 200
    assert resp.data["status"] == JobStatus.ACTIVE


def test_student_sees_only_active_jobs(api_client, student_user, active_job, recruiter_user):
    Job.objects.create(
        company=recruiter_user.companies.first(),
        title="Hidden Draft",
        description="x",
        location="Goa",
        application_deadline=timezone.now() + timedelta(days=3),
        status=JobStatus.DRAFT,
    )
    auth(api_client, student_user)
    resp = api_client.get("/api/jobs/")
    titles = [row["title"] for row in resp.data["results"]]
    assert active_job.title in titles
    assert "Hidden Draft" not in titles


def test_recruiter_cannot_edit_others_job(api_client, other_recruiter, active_job):
    auth(api_client, other_recruiter)
    resp = api_client.put(f"/api/jobs/{active_job.id}/", {"title": "Stolen"}, format="json")
    assert resp.status_code in (403, 404)


def test_job_search_and_location_filter(api_client, student_user, active_job):
    auth(api_client, student_user)
    resp = api_client.get("/api/jobs/?search=Backend")
    assert resp.data["count"] >= 1
    resp = api_client.get("/api/jobs/?location=Bengaluru")
    assert any(row["id"] == active_job.id for row in resp.data["results"])
