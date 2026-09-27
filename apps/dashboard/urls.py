from django.urls import path

from .views import AdminDashboardAPI, MeDashboardAPI, RecruiterDashboardAPI, StudentDashboardAPI

urlpatterns = [
    path("student/", StudentDashboardAPI.as_view(), name="api-dashboard-student"),
    path("recruiter/", RecruiterDashboardAPI.as_view(), name="api-dashboard-recruiter"),
    path("admin/", AdminDashboardAPI.as_view(), name="api-dashboard-admin"),
    path("me/", MeDashboardAPI.as_view(), name="api-dashboard-me"),
]
