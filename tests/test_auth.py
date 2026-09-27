from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.common.constants import Role

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_register_student(api_client):
    resp = api_client.post(
        "/api/auth/register/",
        {
            "email": "new.student@test.local",
            "password": "CampusHire@123",
            "first_name": "New",
            "last_name": "Student",
            "role": "STUDENT",
            "registration_number": "CSE9999",
            "department": "CSE",
            "degree": "BTECH",
            "graduation_year": 2026,
            "cgpa": "8.00",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_201_CREATED
    assert "access" in resp.data
    user = User.objects.get(email="new.student@test.local")
    assert user.role == Role.STUDENT
    assert hasattr(user, "student_profile")


def test_register_rejects_admin_role(api_client):
    resp = api_client.post(
        "/api/auth/register/",
        {
            "email": "hacker@test.local",
            "password": "CampusHire@123",
            "first_name": "X",
            "role": "ADMIN",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_register_password_too_short(api_client):
    resp = api_client.post(
        "/api/auth/register/",
        {
            "email": "short@test.local",
            "password": "x",
            "first_name": "X",
            "role": "RECRUITER",
        },
        format="json",
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_login_success(api_client, student_user, password):
    resp = api_client.post(
        "/api/auth/login/",
        {"email": student_user.email, "password": password},
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.data
    assert resp.data["user"]["role"] == "STUDENT"


def test_login_invalid_password(api_client, student_user):
    resp = api_client.post(
        "/api/auth/login/",
        {"email": student_user.email, "password": "wrong-password"},
        format="json",
    )
    assert resp.status_code == 400


def test_me_requires_auth(api_client):
    resp = api_client.get("/api/auth/me/")
    assert resp.status_code in (401, 403)


def test_change_password(api_client, student_user, password):
    api_client.force_authenticate(student_user)
    resp = api_client.post(
        "/api/auth/password/",
        {"old_password": password, "new_password": "CampusHire@999"},
        format="json",
    )
    assert resp.status_code == 200
    student_user.refresh_from_db()
    assert student_user.check_password("CampusHire@999")
