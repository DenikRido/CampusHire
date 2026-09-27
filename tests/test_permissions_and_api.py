from __future__ import annotations

import pytest

from tests.conftest import auth

pytestmark = pytest.mark.django_db


def test_unauthenticated_jobs_rejected(api_client):
    resp = api_client.get("/api/jobs/")
    assert resp.status_code in (401, 403)


def test_student_profile_me(api_client, student_user):
    auth(api_client, student_user)
    resp = api_client.get("/api/students/me/")
    assert resp.status_code == 200
    assert resp.data["registration_number"] == "CSE0001"


def test_student_cannot_create_company(api_client, student_user):
    auth(api_client, student_user)
    resp = api_client.post("/api/companies/", {"company_name": "Nope Inc"}, format="json")
    assert resp.status_code == 403


def test_recruiter_creates_second_company_rejected(api_client, recruiter_user):
    auth(api_client, recruiter_user)
    resp = api_client.post(
        "/api/companies/",
        {"company_name": "Another Co", "location": "Delhi"},
        format="json",
    )
    assert resp.status_code == 400


def test_pagination_present(api_client, student_user, active_job):
    auth(api_client, student_user)
    resp = api_client.get("/api/jobs/")
    assert "results" in resp.data
    assert "count" in resp.data


def test_schema_available(api_client):
    resp = api_client.get("/api/schema/")
    assert resp.status_code == 200


def test_landing_renders(api_client):
    resp = api_client.get("/")
    assert resp.status_code == 200
    assert b"CampusHire" in resp.content
