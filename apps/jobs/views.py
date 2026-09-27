from __future__ import annotations

from django.core.cache import cache
from django.db.models import Prefetch
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.constants import CompanyVerificationStatus, JobStatus, Role
from apps.common.permissions import IsAdminRole, IsRecruiter, IsRecruiterOrAdmin
from apps.jobs.filters import JobFilter
from apps.jobs.models import Job
from apps.jobs.serializers import JobSerializer, JobStatusSerializer
from apps.jobs.services import check_student_eligibility, invalidate_job_cache, public_job_queryset, transition_job
from apps.notifications.services import create_notification
from apps.students.models import Skill, StudentProfile


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    filterset_class = JobFilter
    search_fields = ["title", "description", "location", "company__company_name"]
    ordering_fields = ["created_at", "application_deadline", "title", "salary_min"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in {"create"}:
            return [IsRecruiter()]
        if self.action in {"update", "partial_update", "destroy"}:
            return [IsRecruiterOrAdmin()]
        if self.action in {"approve", "reject"}:
            return [IsAdminRole()]
        if self.action in {"submit", "close", "activate"}:
            return [IsRecruiterOrAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Job.objects.select_related("company", "company__owner").prefetch_related(
            Prefetch("required_skills", queryset=Skill.objects.all())
        )
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        if user.role == Role.ADMIN:
            return qs
        if user.role == Role.RECRUITER:
            return qs.filter(company__owner=user)
        return public_job_queryset()

    def perform_create(self, serializer):
        user = self.request.user
        company = user.companies.first()
        if company is None:
            raise ValidationError("Create a company profile before posting a job.")
        if company.verification_status != CompanyVerificationStatus.VERIFIED:
            raise ValidationError("Your company must be verified before posting jobs.")
        job = serializer.save(company=company, status=JobStatus.DRAFT)
        invalidate_job_cache()
        return job

    def perform_update(self, serializer):
        job = self.get_object()
        user = self.request.user
        if user.role != Role.ADMIN and job.company.owner_id != user.id:
            raise PermissionDenied("You cannot modify another recruiter's job.")
        if job.status not in {JobStatus.DRAFT, JobStatus.REJECTED, JobStatus.PENDING_APPROVAL} and user.role != Role.ADMIN:
            raise ValidationError("Only draft or rejected jobs can be edited.")
        serializer.save()
        invalidate_job_cache()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role != Role.ADMIN and instance.company.owner_id != user.id:
            raise PermissionDenied("You cannot delete this job.")
        if instance.status == JobStatus.ACTIVE and instance.applications.exists():
            raise ValidationError("Close the job instead of deleting it once applications exist.")
        instance.delete()
        invalidate_job_cache()

    @action(detail=True, methods=["get"], url_path="eligibility")
    def eligibility(self, request, pk=None):
        job = self.get_object() if request.user.role != Role.STUDENT else (
            Job.objects.select_related("company").prefetch_related("required_skills").get(pk=pk)
        )
        if request.user.role != Role.STUDENT:
            return Response({"detail": "Eligibility is evaluated for student profiles."}, status=400)
        profile = StudentProfile.objects.filter(user=request.user).first()
        if not profile:
            return Response({"eligible": False, "reasons": ["Complete your student profile first."]})
        result = check_student_eligibility(profile, job)
        return Response(result.as_dict())

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        job = self.get_object()
        try:
            job = transition_job(job, JobStatus.PENDING_APPROVAL, actor=request.user)
        except (ValueError, PermissionError) as exc:
            raise ValidationError(str(exc))
        return Response(JobSerializer(job).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        job = self.get_object()
        try:
            job = transition_job(job, JobStatus.APPROVED, actor=request.user)
        except (ValueError, PermissionError) as exc:
            raise ValidationError(str(exc))
        create_notification(
            recipient=job.company.owner,
            title="Job approved",
            message=f"{job.title} is now live for students.",
            notification_type="JOB",
        )
        return Response(JobSerializer(job).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        serializer = JobStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = self.get_object()
        try:
            job = transition_job(
                job,
                JobStatus.REJECTED,
                actor=request.user,
                reason=serializer.validated_data.get("reason", ""),
            )
        except (ValueError, PermissionError) as exc:
            raise ValidationError(str(exc))
        create_notification(
            recipient=job.company.owner,
            title="Job rejected",
            message=f"{job.title} was rejected. {job.rejection_reason}",
            notification_type="JOB",
        )
        return Response(JobSerializer(job).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        job = self.get_object()
        try:
            job = transition_job(job, JobStatus.CLOSED, actor=request.user)
        except (ValueError, PermissionError) as exc:
            raise ValidationError(str(exc))
        return Response(JobSerializer(job).data)

    @action(detail=False, methods=["get"], url_path="public")
    def public_list(self, request):
        """Public cached listing used by the jobs page JS."""
        cached = cache.get("jobs:public:list:v1")
        # Filtering/search skip the unfiltered cache.
        if request.query_params and cached is None:
            pass
        qs = public_job_queryset()
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        serializer = JobSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
