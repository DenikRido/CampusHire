from __future__ import annotations

from django.shortcuts import get_object_or_404, render

from apps.applications.models import Application
from apps.common.decorators import recruiter_required
from apps.companies.models import Company
from apps.interviews.models import Interview
from apps.jobs.models import Job
from apps.notifications.models import Notification
from apps.recruiters.models import RecruiterProfile
from apps.students.models import Skill


@recruiter_required
def dashboard(request):
    company = Company.objects.filter(owner=request.user).first()
    return render(request, "recruiter/dashboard.html", {"company": company})


@recruiter_required
def company(request):
    company = Company.objects.filter(owner=request.user).first()
    profile, _ = RecruiterProfile.objects.get_or_create(user=request.user)
    return render(request, "recruiter/company.html", {"company": company, "profile": profile})


@recruiter_required
def jobs(request):
    jobs = Job.objects.filter(company__owner=request.user).select_related("company")
    return render(request, "recruiter/jobs.html", {"jobs": jobs})


@recruiter_required
def job_create(request):
    skills = Skill.objects.all()
    return render(request, "recruiter/job_form.html", {"job": None, "skills": skills})


@recruiter_required
def job_edit(request, pk: int):
    job = get_object_or_404(Job, pk=pk, company__owner=request.user)
    skills = Skill.objects.all()
    return render(request, "recruiter/job_form.html", {"job": job, "skills": skills})


@recruiter_required
def applicants(request, pk: int):
    job = get_object_or_404(Job, pk=pk, company__owner=request.user)
    return render(request, "recruiter/applicants.html", {"job": job})


@recruiter_required
def applicant_detail(request, pk: int):
    application = get_object_or_404(
        Application.objects.select_related("student__user", "job__company").prefetch_related(
            "history", "student__student_skills__skill"
        ),
        pk=pk,
        job__company__owner=request.user,
    )
    return render(request, "recruiter/applicant_detail.html", {"application": application})


@recruiter_required
def interviews(request):
    items = Interview.objects.filter(application__job__company__owner=request.user).select_related(
        "application__job", "application__student__user"
    )
    return render(request, "recruiter/interviews.html", {"interviews": items})


@recruiter_required
def notifications(request):
    items = Notification.objects.filter(recipient=request.user)[:50]
    return render(request, "recruiter/notifications.html", {"notifications": items})
