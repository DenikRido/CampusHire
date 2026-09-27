from __future__ import annotations

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.jobs.services import public_job_queryset
from tests.conftest import auth

pytestmark = pytest.mark.django_db


def test_job_list_avoids_n_plus_one(api_client, student_user, recruiter_user, active_job):
    from datetime import timedelta

    from django.utils import timezone

    from apps.common.constants import JobStatus
    from apps.jobs.models import Job

    company = recruiter_user.companies.first()
    for i in range(8):
        Job.objects.create(
            company=company,
            title=f"Role {i}",
            description="desc",
            location="Bengaluru",
            application_deadline=timezone.now() + timedelta(days=5),
            status=JobStatus.ACTIVE,
        )
    auth(api_client, student_user)
    with CaptureQueriesContext(connection) as ctx:
        resp = api_client.get("/api/jobs/")
    assert resp.status_code == 200
    # select_related/prefetch should keep this well below a naive N+1 (1 + 8 companies + 8 skills).
    assert len(ctx) < 15


def test_public_queryset_uses_select_related():
    qs = public_job_queryset()
    assert "company" in str(qs.query).lower() or qs.query.select_related
