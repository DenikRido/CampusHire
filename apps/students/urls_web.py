from django.urls import path

from . import views_web

urlpatterns = [
    path("dashboard/", views_web.dashboard, name="student-dashboard"),
    path("profile/", views_web.profile, name="student-profile"),
    path("resume/", views_web.resume, name="student-resume"),
    path("skills/", views_web.skills, name="student-skills"),
    path("jobs/", views_web.jobs, name="student-jobs"),
    path("jobs/<int:pk>/", views_web.job_detail, name="student-job-detail"),
    path("jobs/<int:pk>/apply/", views_web.apply, name="student-apply"),
    path("applications/", views_web.applications, name="student-applications"),
    path("applications/<int:pk>/", views_web.application_detail, name="student-application-detail"),
    path("interviews/", views_web.interviews, name="student-interviews"),
    path("notifications/", views_web.notifications, name="student-notifications"),
]
