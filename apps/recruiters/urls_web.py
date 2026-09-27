from django.urls import path

from . import views_web

urlpatterns = [
    path("dashboard/", views_web.dashboard, name="recruiter-dashboard"),
    path("company/", views_web.company, name="recruiter-company"),
    path("jobs/", views_web.jobs, name="recruiter-jobs"),
    path("jobs/new/", views_web.job_create, name="recruiter-job-create"),
    path("jobs/<int:pk>/edit/", views_web.job_edit, name="recruiter-job-edit"),
    path("jobs/<int:pk>/applicants/", views_web.applicants, name="recruiter-applicants"),
    path("applications/<int:pk>/", views_web.applicant_detail, name="recruiter-applicant-detail"),
    path("interviews/", views_web.interviews, name="recruiter-interviews"),
    path("notifications/", views_web.notifications, name="recruiter-notifications"),
]
