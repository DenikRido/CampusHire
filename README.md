# CampusHire

Campus placement and recruitment management platform.

CampusHire is a modular Django monolith for campus hiring. Students apply to jobs only when they meet eligibility rules. Recruiters manage company profiles, jobs, applicants, and interviews. Admins verify companies, approve postings, and read placement reports. The same business services power both Django templates and a JWT-protected REST API.

## Problem

Campus placement teams still run hiring on spreadsheets: eligibility is checked by hand, application status is lost in email, and recruiters cannot see a clean pipeline. CampusHire encodes those rules in the backend so the UI cannot bypass them.

## Features

- Custom user model with `STUDENT`, `RECRUITER`, and `ADMIN` roles
- Student profiles, skills, education, and validated resume upload (PDF/DOCX)
- Recruiter company profiles with admin verification
- Job workflow: draft → pending approval → approved/active → closed (or rejected)
- Eligibility engine with structured failure reasons
- Applications with unique `(student, job)` constraint and status history
- Interview scheduling with access control
- In-app notifications (written in the request transaction; email via Celery)
- Role-specific dashboards loaded from REST APIs
- Admin reports via ORM aggregations
- Swagger/OpenAPI at `/api/docs/`
- Redis caching for dashboard summaries
- Celery beat task that closes expired jobs
- Docker Compose: MySQL, Redis, Gunicorn, Celery worker, Nginx

## User roles

| Role | Can | Cannot |
| --- | --- | --- |
| Student | Manage profile/resume/skills, browse jobs, check eligibility, apply, withdraw (early states), view interviews and notifications | Create companies or jobs, see other students’ private data |
| Recruiter | Manage own company and jobs, review applicants, change status, schedule interviews | Touch another recruiter’s jobs or admin tools |
| Admin | Verify companies, approve/reject jobs, view all applications, reports, users | — |

Authorization is enforced in DRF permission classes and Django view decorators, not only by hiding buttons.

## Technology stack

- Python 3.12 / Django 5.1 / Django REST Framework
- MySQL 8 (SQLite is used only for automated tests)
- Redis, Celery
- SimpleJWT, django-filter, drf-spectacular
- Django templates, HTML5, CSS3, Bootstrap 5, vanilla JavaScript (`fetch`)
- Gunicorn, Nginx, Docker Compose
- pytest / pytest-django

## Architecture

```
Browser  →  Django templates + JS fetch()
         →  DRF (JWT or session + CSRF)
         →  Service layer (eligibility, applications, interviews)
         →  Django ORM  →  MySQL
Background: Celery worker ← Redis  (email, close expired jobs)
Cache: Redis (dashboard keys are per-user; public job list is non-private)
```

Apps live under `apps/`: `accounts`, `students`, `recruiters`, `companies`, `jobs`, `applications`, `interviews`, `notifications`, `dashboard`, `common`.

Settings are split: `config.settings.base`, `.development`, `.production`, `.test`.

## Database design

Custom `User` (email login) plus:

- `StudentProfile` 1–1 User, `Education`, `Skill`, `StudentSkill`
- `RecruiterProfile` 1–1 User, `Company` owned by a recruiter
- `Job` with JSON eligibility lists, M2M required skills, indexed status/deadline/location/title
- `Application` unique together `(student, job)`
- `ApplicationStatusHistory`
- `Interview`, `Notification`

See models in `apps/*/models.py`.

## API documentation

Interactive docs: `/api/docs/`  
Schema: `/api/schema/`

Authenticate in Swagger with `Bearer <access_token>` from `POST /api/auth/login/`.

### Auth

| Method | Path |
| --- | --- |
| POST | `/api/auth/register/` |
| POST | `/api/auth/login/` |
| POST | `/api/auth/refresh/` |
| GET | `/api/auth/me/` |
| POST | `/api/auth/password/` |

### Domain

| Method | Path |
| --- | --- |
| GET/PUT | `/api/students/me/` |
| GET/POST | `/api/students/me/skills/` |
| POST | `/api/students/me/resume/` |
| GET/POST/PUT | `/api/jobs/` and `/api/jobs/{id}/` |
| GET | `/api/jobs/{id}/eligibility/` |
| POST | `/api/jobs/{id}/submit/`, `/approve/`, `/reject/`, `/close/` |
| POST/GET | `/api/applications/` |
| PATCH | `/api/applications/{id}/status/` |
| POST | `/api/applications/{id}/withdraw/` |
| GET/POST/PATCH | `/api/interviews/` |
| GET | `/api/notifications/` |
| PATCH | `/api/notifications/{id}/read/` |
| GET/POST/PUT | `/api/companies/` |
| POST | `/api/companies/{id}/verify/` |
| GET | `/api/dashboard/student/`, `/recruiter/`, `/admin/` |

Filtering example: `GET /api/jobs/?search=python&location=Chennai&department=CSE&page=2`

## Folder structure

```
campushire/
  config/                 Django project (settings, urls, celery, wsgi)
  apps/                   Domain apps + service layers
  templates/              Django templates (public, student, recruiter, admin)
  static/css|js           Design tokens, fetch() clients
  tests/                  pytest suite
  nginx/nginx.conf
  Dockerfile
  docker-compose.yml
  manage.py
```

## Environment

Copy `.env.example` to `.env` and set `SECRET_KEY`, database passwords, and `ALLOWED_HOSTS`. Never commit `.env`.

## Local setup (without Docker)

Requires Python 3.11+ and MySQL 8.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
# point DB_* at your MySQL instance
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py migrate
python manage.py seed_data
python manage.py runserver 0.0.0.0:8000
```

Optional Redis:

```bash
export USE_REDIS_CACHE=1 REDIS_URL=redis://127.0.0.1:6379/0
celery -A config worker -l info
celery -A config beat -l info
```

If Redis is down, development settings use locmem cache and eager Celery. In-app notifications still persist in MySQL because they are written in the request transaction; only email delivery is asynchronous.

## Docker setup

```bash
cp .env.example .env
# set SECRET_KEY, DB_PASSWORD, ALLOWED_HOSTS
docker compose up --build
```

Nginx serves port 80, Gunicorn is upstream, MySQL and Redis are health-checked before migrate. `SEED_ON_START=1` loads demo data on first boot.

## Seed data / demo credentials

`python manage.py seed_data` (idempotent enough to re-run).

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@campushire.local` | `CampusHire@123` |
| Student | `priya.sharma@campushire.local` | `CampusHire@123` |
| Recruiter | `rec.nimbus@campushire.local` | `CampusHire@123` |

These passwords exist only for local demonstration.

## Tests

```bash
pytest
```

Tests use in-memory SQLite (`config.settings.test`) so CI does not require MySQL. Models stay MySQL-compatible (no SQLite-only features).

## Swagger

`/api/docs/` after the server is running.

## Deployment

1. Provision a VM or container host.
2. Set production environment variables (see `.env.example`). `DEBUG` must be `0`.
3. `docker compose up -d --build`.
4. Put TLS in front of Nginx (load balancer or Certbot) and set `SESSION_COOKIE_SECURE=1`, `CSRF_COOKIE_SECURE=1`, `SECURE_SSL_REDIRECT=1`, `SECURE_HSTS_SECONDS`.
5. Point `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` at the public hostname.
6. Store resumes on object storage before scaling to multiple web instances (current `FileSystemStorage` is local disk).

## Security notes

- CSRF middleware stays on; JS sends `X-CSRFToken`
- Passwords hashed with Django’s hasher; validators require 10+ characters
- Secrets come from the environment
- Resume upload checks extension, MIME, size, and magic bytes
- ORM used for all queries
- Production settings refuse to start without `SECRET_KEY` and `ALLOWED_HOSTS`
- Role checks on every mutating API

## Performance

- PageNumber pagination (10, max 50)
- Indexes on job status/deadline/location/title, application status, student department/year, company verification
- `select_related` / `prefetch_related` on job, application, and interview querysets
- Redis cache for per-user dashboard payloads (30s) and job-list invalidation on writes
- Dashboard reports use `Count` aggregations rather than Python loops over full rows (department JSON is the documented exception)

## Screenshots

Add product screenshots here after a local run:

- Landing
- Student job list (API-driven)
- Eligibility panel
- Recruiter applicant pipeline
- Admin reports

## Scalability (documented, not over-built)

This is a modular monolith. Later scale-out options:

- More Gunicorn workers, then multiple web replicas behind Nginx/load balancer
- Separate Celery worker pool
- Redis for cache + broker
- MySQL read replicas for dashboards
- Object storage for resumes
- Do **not** split into microservices until a bounded context actually needs independent deploy

## Future improvements

- Object storage (S3) for resumes
- Token blacklist / logout of JWT
- Fine-grained audit log UI
- Full-text search (MySQL FULLTEXT or OpenSearch)
- Calendar invites for interviews

## Suggested Git commits

See `DEVELOPMENT.md`.

## License

Use and modify for portfolio / educational purposes.
