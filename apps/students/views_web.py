from __future__ import annotations

from django.shortcuts import get_object_or_404, render

from apps.common.decorators import student_required
from apps.jobs.models import Job
from apps.jobs.services import public_job_queryset
from apps.applications.models import Application
from apps.interviews.models import Interview
from apps.notifications.models import Notification
from apps.students.models import StudentProfile


def _profile(user):
    return StudentProfile.objects.filter(user=user).first()


@student_required
def dashboard(request):
    return render(request, "student/dashboard.html", {"profile": _profile(request.user)})


@student_required
def profile(request):
    return render(request, "student/profile.html", {"profile": _profile(request.user)})


@student_required
def resume(request):
    return render(request, "student/resume.html", {"profile": _profile(request.user)})


@student_required
def skills(request):
    profile = _profile(request.user)
    skills = profile.student_skills.select_related("skill") if profile else []
    return render(request, "student/skills.html", {"profile": profile, "skills": skills})


@student_required
def jobs(request):
    return render(request, "student/jobs.html")


@student_required
def job_detail(request, pk: int):
    job = get_object_or_404(public_job_queryset(), pk=pk)
    return render(request, "student/job_detail.html", {"job": job})


@student_required
def apply(request, pk: int):
    job = get_object_or_404(Job.objects.select_related("company"), pk=pk)
    return render(request, "student/apply.html", {"job": job})


@student_required
def applications(request):
    return render(request, "student/applications.html")


@student_required
def application_detail(request, pk: int):
    application = get_object_or_404(
        Application.objects.select_related("job__company", "student"),
        pk=pk,
        student__user=request.user,
    )
    return render(request, "student/application_detail.html", {"application": application})


@student_required
def interviews(request):
    items = (
        Interview.objects.filter(application__student__user=request.user)
        .select_related("application__job__company")
        .order_by("scheduled_at")
    )
    return render(request, "student/interviews.html", {"interviews": items})


@student_required
def notifications(request):
    items = Notification.objects.filter(recipient=request.user)[:50]
    return render(request, "student/notifications.html", {"notifications": items})
