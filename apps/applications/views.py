from __future__ import annotations

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.applications.models import Application
from apps.applications.serializers import ApplicationSerializer, ApplicationStatusUpdateSerializer
from apps.applications.services import apply_to_job, change_application_status, recruiter_owns_application, withdraw_application
from apps.common.constants import Role
from apps.common.exceptions import ConflictError, EligibilityError
from apps.common.permissions import IsAuthenticatedAndActive
from apps.jobs.models import Job
from apps.students.models import StudentProfile


class ApplicationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticatedAndActive]
    filterset_fields = ["status", "job"]
    search_fields = ["job__title", "student__user__email", "student__registration_number"]
    ordering_fields = ["applied_at", "status"]

    def get_queryset(self):
        qs = Application.objects.select_related(
            "student__user",
            "job__company",
        ).prefetch_related("history", "job__required_skills")
        user = self.request.user
        if user.role == Role.ADMIN:
            return qs
        if user.role == Role.RECRUITER:
            return qs.filter(job__company__owner=user)
        return qs.filter(student__user=user)

    def create(self, request, *args, **kwargs):
        if request.user.role != Role.STUDENT:
            raise PermissionDenied("Only students can apply for jobs.")
        profile = StudentProfile.objects.filter(user=request.user).first()
        if not profile:
            raise ValidationError("Complete your student profile first.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            job = Job.objects.select_related("company").prefetch_related("required_skills").get(
                pk=serializer.validated_data["job_id"]
            )
        except Job.DoesNotExist as exc:
            raise ValidationError("Job not found.") from exc
        try:
            application = apply_to_job(
                student=profile,
                job=job,
                cover_letter=serializer.validated_data.get("cover_letter", ""),
            )
        except EligibilityError as exc:
            return Response(
                {"success": False, "eligible": False, "reasons": exc.reasons, "message": "Not eligible."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ConflictError as exc:
            return Response({"detail": str(exc.detail)}, status=status.HTTP_409_CONFLICT)
        out = ApplicationSerializer(application, context={"request": request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        application = self.get_object()
        if request.user.role not in {Role.RECRUITER, Role.ADMIN}:
            raise PermissionDenied("Only recruiters can update application status.")
        if not recruiter_owns_application(request.user, application):
            raise PermissionDenied("This application does not belong to your jobs.")
        serializer = ApplicationStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            application = change_application_status(
                application=application,
                new_status=serializer.validated_data["status"],
                actor=request.user,
                remarks=serializer.validated_data.get("remarks", ""),
            )
        except ValueError as exc:
            raise ValidationError(str(exc))
        return Response(ApplicationSerializer(application, context={"request": request}).data)

    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        application = self.get_object()
        try:
            application = withdraw_application(application=application, actor=request.user)
        except (ValueError, PermissionError) as exc:
            raise ValidationError(str(exc))
        return Response(ApplicationSerializer(application, context={"request": request}).data)
