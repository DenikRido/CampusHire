"""Test settings: SQLite, locmem cache, eager Celery, fast hashing."""
from __future__ import annotations

from .base import *  # noqa: F403

DEBUG = True
SECRET_KEY = "test-secret-key-not-for-production-32b+"

DATABASES = {  # noqa: F811
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

CACHES = {  # noqa: F811
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "campushire-test",
    }
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
MEDIA_ROOT = BASE_DIR / "media_test"  # noqa: F405

LOGGING["root"]["level"] = "WARNING"  # noqa: F405
