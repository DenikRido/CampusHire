"""Local development settings. Safe defaults, no production hardening."""
from __future__ import annotations

from django.core.management.utils import get_random_secret_key

from .base import *  # noqa: F403
from .base import env, env_bool, env_list

DEBUG = env_bool("DEBUG", True)

if not SECRET_KEY:  # noqa: F405
    SECRET_KEY = env("SECRET_KEY", "dev-only-not-for-production-" + get_random_secret_key()[:24])

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0,*")

if not env_bool("USE_REDIS_CACHE", False):
    CACHES = {  # noqa: F811
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "campushire-dev",
        }
    }

CELERY_TASK_ALWAYS_EAGER = env_bool("CELERY_TASK_ALWAYS_EAGER", True)

EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

# Live preview is iframed; allow embedding in development only.
X_FRAME_OPTIONS = "ALLOWALL"

LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405
