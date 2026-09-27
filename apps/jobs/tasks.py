from __future__ import annotations

import logging

from celery import shared_task
from django.utils import timezone

from apps.common.constants import JobStatus
from apps.jobs.models import Job
from apps.jobs.services import invalidate_job_cache

logger = logging.getLogger("apps")


@shared_task(name="apps.jobs.tasks.close_expired_jobs")
def close_expired_jobs() -> int:
    now = timezone.now()
    updated = Job.objects.filter(status=JobStatus.ACTIVE, application_deadline__lt=now).update(
        status=JobStatus.CLOSED
    )
    if updated:
        invalidate_job_cache()
        logger.info("Closed %s expired jobs", updated)
    return updated
