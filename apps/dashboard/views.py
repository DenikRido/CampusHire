from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.constants import Role
from apps.common.permissions import IsAdminRole, IsRecruiter, IsStudent
from apps.dashboard.services import admin_dashboard, recruiter_dashboard, student_dashboard


class StudentDashboardAPI(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        return Response(student_dashboard(request.user))


class RecruiterDashboardAPI(APIView):
    permission_classes = [IsRecruiter]

    def get(self, request):
        return Response(recruiter_dashboard(request.user))


class AdminDashboardAPI(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        return Response(admin_dashboard())


class MeDashboardAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == Role.STUDENT:
            return Response(student_dashboard(request.user))
        if request.user.role == Role.RECRUITER:
            return Response(recruiter_dashboard(request.user))
        if request.user.role == Role.ADMIN:
            return Response(admin_dashboard())
        return Response({})
