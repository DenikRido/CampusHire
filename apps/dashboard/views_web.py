from __future__ import annotations

from django.contrib.auth import get_user_model
from django.shortcuts import render

from apps.applications.models import Application
from apps.common.decorators import admin_required
from apps.companies.models import Company
from apps.jobs.models import Job
from apps.notifications.models import Notification

User = get_user_model()


@admin_required
def dashboard(request):
    return render(request, "admin_panel/dashboard.html")


@admin_required
def users(request):
    users = User.objects.all().order_by("-date_joined")[:200]
    return render(request, "admin_panel/users.html", {"users": users})


@admin_required
def companies(request):
    companies = Company.objects.select_related("owner").all()
    return render(request, "admin_panel/companies.html", {"companies": companies})


@admin_required
def jobs(request):
    jobs = Job.objects.select_related("company").all()
    return render(request, "admin_panel/jobs.html", {"jobs": jobs})


@admin_required
def applications(request):
    applications = Application.objects.select_related("student__user", "job__company")[:200]
    return render(request, "admin_panel/applications.html", {"applications": applications})


@admin_required
def reports(request):
    return render(request, "admin_panel/reports.html")


@admin_required
def notifications(request):
    items = Notification.objects.filter(recipient=request.user)[:50]
    return render(request, "admin_panel/notifications.html", {"notifications": items})
