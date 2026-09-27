"""Aggregated dashboard statistics. Cached briefly; never cache across users."""
from __future__ import annotations

from django.core.cache import cache
from django.db.models import Count, Q
from django.utils import timezone

from apps.applications.models import Application
from apps.common.constants import ApplicationStatus, JobStatus, Role
from apps.companies.models import Company
from apps.interviews.models import Interview
from apps.jobs.models import Job
from apps.notifications.models import Notification
from apps.students.models import StudentProfile


def student_dashboard(user) -> dict:
    cache_key = f"dashboard:student:{user.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    profile = StudentProfile.objects.filter(user=user).first()
    apps_qs = Application.objects.filter(student=profile) if profile else Application.objects.none()
    now = timezone.now()
    data = {
        "active_applications": apps_qs.exclude(
            status__in=[ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN, ApplicationStatus.SELECTED]
        ).count(),
        "shortlisted": apps_qs.filter(status=ApplicationStatus.SHORTLISTED).count(),
        "selected": apps_qs.filter(status=ApplicationStatus.SELECTED).count(),
        "upcoming_interviews": Interview.objects.filter(
            application__student=profile, scheduled_at__gte=now
        ).count()
        if profile
        else 0,
        "unread_notifications": Notification.objects.filter(recipient=user, is_read=False).count(),
        "available_jobs": Job.objects.filter(
            status=JobStatus.ACTIVE, application_deadline__gte=now
        ).count(),
        "total_applications": apps_qs.count(),
    }
    cache.set(cache_key, data, 30)
    return data


def recruiter_dashboard(user) -> dict:
    cache_key = f"dashboard:recruiter:{user.id}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    jobs = Job.objects.filter(company__owner=user)
    apps = Application.objects.filter(job__company__owner=user)
    now = timezone.now()
    data = {
        "active_jobs": jobs.filter(status=JobStatus.ACTIVE).count(),
        "total_jobs": jobs.count(),
        "total_applications": apps.count(),
        "shortlisted_candidates": apps.filter(status=ApplicationStatus.SHORTLISTED).count(),
        "scheduled_interviews": Interview.objects.filter(
            application__job__company__owner=user, scheduled_at__gte=now
        ).count(),
        "selected_candidates": apps.filter(status=ApplicationStatus.SELECTED).count(),
        "unread_notifications": Notification.objects.filter(recipient=user, is_read=False).count(),
        "pending_approval_jobs": jobs.filter(status=JobStatus.PENDING_APPROVAL).count(),
    }
    cache.set(cache_key, data, 30)
    return data


def admin_dashboard() -> dict:
    cache_key = "dashboard:admin"
    cached = cache.get(cache_key)
    if cached:
        return cached
    from django.contrib.auth import get_user_model

    User = get_user_model()
    apps = Application.objects.all()
    data = {
        "total_students": User.objects.filter(role=Role.STUDENT).count(),
        "total_recruiters": User.objects.filter(role=Role.RECRUITER).count(),
        "total_companies": Company.objects.count(),
        "verified_companies": Company.objects.filter(verification_status="VERIFIED").count(),
        "active_jobs": Job.objects.filter(status=JobStatus.ACTIVE).count(),
        "pending_job_approvals": Job.objects.filter(status=JobStatus.PENDING_APPROVAL).count(),
        "total_applications": apps.count(),
        "selected_candidates": apps.filter(status=ApplicationStatus.SELECTED).count(),
        "applications_by_status": list(
            apps.values("status").annotate(count=Count("id")).order_by("status")
        ),
        "jobs_by_department": _jobs_by_department(),
        "applications_by_company": list(
            apps.values("job__company__company_name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        ),
        "interview_count": Interview.objects.count(),
        "placement_rate": _placement_rate(apps),
    }
    cache.set(cache_key, data, 30)
    return data


def _jobs_by_department() -> list[dict]:
    """Count active jobs whose eligibility includes each department code."""
    from apps.common.constants import Department

    jobs = list(Job.objects.filter(status=JobStatus.ACTIVE).values_list("eligible_departments", flat=True))
    counts: dict[str, int] = {code: 0 for code, _ in Department.choices}
    for departments in jobs:
        if not departments:
            for code in counts:
                counts[code] += 1
        else:
            for code in departments:
                if code in counts:
                    counts[code] += 1
    return [{"department": k, "count": v} for k, v in counts.items() if v]


def _placement_rate(apps) -> float:
    total = apps.count()
    if not total:
        return 0.0
    selected = apps.filter(status=ApplicationStatus.SELECTED).count()
    return round((selected / total) * 100, 1)
