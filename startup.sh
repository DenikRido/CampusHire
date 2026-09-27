#!/bin/sh
set -eu
cd /workspace
export PATH="$HOME/.local/bin:$PATH"
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.development}"
export DB_ENGINE="${DB_ENGINE:-sqlite}"
export SQLITE_PATH="${SQLITE_PATH:-/workspace/db.sqlite3}"
export DEBUG="${DEBUG:-1}"
export SECRET_KEY="${SECRET_KEY:-dev-only-campushire-preview-key}"
export USE_REDIS_CACHE="${USE_REDIS_CACHE:-0}"
export CELERY_TASK_ALWAYS_EAGER="${CELERY_TASK_ALWAYS_EAGER:-1}"
export PYTHONUNBUFFERED=1
export ALLOWED_HOSTS="${ALLOWED_HOSTS:-localhost,127.0.0.1,0.0.0.0,*}"

if curl -sf -o /dev/null --max-time 2 http://127.0.0.1:8080/healthz; then
  exit 0
fi

python3 manage.py migrate --noinput >>/tmp/app-startup.log 2>&1
python3 manage.py seed_data >>/tmp/app-startup.log 2>&1 || true
python3 manage.py collectstatic --noinput >>/tmp/app-startup.log 2>&1 || true
python3 manage.py runserver 0.0.0.0:8080 >>/tmp/app-startup.log 2>&1 &
