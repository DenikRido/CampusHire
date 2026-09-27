from django.urls import path

from . import views_web

urlpatterns = [
    path("", views_web.dashboard, name="admin-dashboard"),
    path("users/", views_web.users, name="admin-users"),
    path("companies/", views_web.companies, name="admin-companies"),
    path("jobs/", views_web.jobs, name="admin-jobs"),
    path("applications/", views_web.applications, name="admin-applications"),
    path("reports/", views_web.reports, name="admin-reports"),
    path("notifications/", views_web.notifications, name="admin-notifications"),
]
