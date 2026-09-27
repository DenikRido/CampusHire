from __future__ import annotations

from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.applications.models import Application
from apps.applications.services import recruiter_owns_application
from apps.common.constants import Role
from apps.common.permissions import IsAuthenticatedAndActive
from apps.interviews.models import Interview
from apps.interviews.serializers import InterviewSerializer
from apps.interviews.services import schedule_interview, update_interview


class InterviewViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticatedAndActive]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        qs = Interview.objects.select_related(
            "application__job__company",
            "application__student__user",
        )
        user = self.request.user
        if user.role == Role.ADMIN:
            return qs
        if user.role == Role.RECRUITER:
            return qs.filter(application__job__company__owner=user)
        return qs.filter(application__student__user=user)

    def create(self, request, *args, **kwargs):
        if request.user.role not in {Role.RECRUITER, Role.ADMIN}:
            raise PermissionDenied("Only recruiters can schedule interviews.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            application = Application.objects.select_related("job__company", "student__user").get(
                pk=serializer.validated_data["application_id"]
            )
        except Application.DoesNotExist as exc:
            raise ValidationError("Application not found.") from exc
        if not recruiter_owns_application(request.user, application):
            raise PermissionDenied("This candidate did not apply to your job.")
        try:
            interview = schedule_interview(
                application=application,
                scheduled_at=serializer.validated_data["scheduled_at"],
                mode=serializer.validated_data.get("mode", "ONLINE"),
                interviewer_name=serializer.validated_data["interviewer_name"],
                meeting_link=serializer.validated_data.get("meeting_link", ""),
                location=serializer.validated_data.get("location", ""),
                notes=serializer.validated_data.get("notes", ""),
                actor=request.user,
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(InterviewSerializer(interview).data, status=201)

    def partial_update(self, request, *args, **kwargs):
        interview = self.get_object()
        if request.user.role == Role.STUDENT:
            raise PermissionDenied("Students cannot modify interviews.")
        if request.user.role == Role.RECRUITER and not recruiter_owns_application(
            request.user, interview.application
        ):
            raise PermissionDenied("You cannot modify this interview.")
        serializer = self.get_serializer(interview, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            interview = update_interview(interview=interview, actor=request.user, **serializer.validated_data)
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(InterviewSerializer(interview).data)
