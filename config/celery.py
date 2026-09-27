"""Celery application for CampusHire background work."""
from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("campushire")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "close-expired-jobs-hourly": {
        "task": "apps.jobs.tasks.close_expired_jobs",
        "schedule": 60 * 60,
    },
}
app.conf.timezone = "UTC"
