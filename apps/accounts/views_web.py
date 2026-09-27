from __future__ import annotations

from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.common.constants import Role


def landing_page(request):
    if request.user.is_authenticated:
        return redirect("app-home")
    return render(request, "public/landing.html")


def about_page(request):
    return render(request, "public/about.html")


@require_http_methods(["GET", "POST"])
def login_page(request):
    if request.user.is_authenticated:
        return redirect("app-home")
    return render(request, "public/login.html")


@require_http_methods(["GET", "POST"])
def register_page(request):
    if request.user.is_authenticated:
        return redirect("app-home")
    return render(request, "public/register.html")


def logout_view(request):
    logout(request)
    return redirect("landing")


def post_login_redirect(request):
    if not request.user.is_authenticated:
        return redirect("login")
    if request.user.role == Role.STUDENT:
        return redirect("student-dashboard")
    if request.user.role == Role.RECRUITER:
        return redirect("recruiter-dashboard")
    return redirect("admin-dashboard")
