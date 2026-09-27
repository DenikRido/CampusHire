# Development notes

## Suggested commit plan

1. Initial Django project layout and settings split
2. Custom user authentication and JWT
3. Student profile, skills, resume validation
4. Recruiter and company verification
5. Job workflow and eligibility engine
6. Application workflow, unique constraint, status history
7. Interviews and notifications (Celery email)
8. REST API, permissions, filters, pagination
9. Django templates + JavaScript fetch integration
10. Redis caching and dashboard aggregations
11. pytest coverage for auth, eligibility, applications
12. Docker, Nginx, Gunicorn, Celery worker
13. OpenAPI documentation and README

## Interview talking points mapped to code

| Question | Where to look |
| --- | --- |
| Why a service layer? | `apps/jobs/services.py`, `apps/applications/services.py` |
| Eligibility engine | `check_student_eligibility` |
| Duplicate applications | `UniqueConstraint` on `Application` + `IntegrityError` → 409 |
| Status transitions | `APPLICATION_TRANSITIONS` in `apps/common/constants.py` |
| JWT + session | `REST_FRAMEWORK` auth classes; login view issues both |
| Caching | `apps/dashboard/services.py` keys include user id |
| Celery | Notification row is sync; `send_notification_email` is async |
| N+1 | Job/Application querysets + `tests/test_performance.py` |
| Permissions | `apps/common/permissions.py` |
