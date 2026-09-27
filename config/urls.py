"""Root URL configuration."""
from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.accounts.views_web import (
    about_page,
    landing_page,
    login_page,
    logout_view,
    post_login_redirect,
    register_page,
)
from apps.common.views import healthz

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz, name="healthz"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/students/", include("apps.students.urls")),
    path("api/recruiters/", include("apps.recruiters.urls")),
    path("api/companies/", include("apps.companies.urls")),
    path("api/jobs/", include("apps.jobs.urls")),
    path("api/applications/", include("apps.applications.urls")),
    path("api/interviews/", include("apps.interviews.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("", landing_page, name="landing"),
    path("about/", about_page, name="about"),
    path("login/", login_page, name="login"),
    path("register/", register_page, name="register"),
    path("logout/", logout_view, name="logout"),
    path("app/", post_login_redirect, name="app-home"),
    path("student/", include("apps.students.urls_web")),
    path("recruiter/", include("apps.recruiters.urls_web")),
    path("admin-panel/", include("apps.dashboard.urls_web")),
]

handler403 = "apps.common.views.handler403"
handler404 = "apps.common.views.handler404"
handler500 = "apps.common.views.handler500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
