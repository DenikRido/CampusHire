from __future__ import annotations

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.constants import Role
from apps.common.permissions import IsAdminRole, IsRecruiter
from apps.notifications.services import create_notification

from .models import Company
from .serializers import CompanySerializer, CompanyVerificationSerializer


class CompanyViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Company.objects.select_related("owner").all()
    serializer_class = CompanySerializer
    filterset_fields = ["verification_status", "industry", "location"]
    search_fields = ["company_name", "industry", "location", "description"]
    ordering_fields = ["company_name", "created_at"]

    def get_permissions(self):
        if self.action == "create":
            return [IsRecruiter()]
        if self.action in {"update", "partial_update"}:
            return [IsAuthenticated()]
        if self.action == "verify":
            return [IsAdminRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
        if user.role == Role.ADMIN:
            return qs
        if user.role == Role.RECRUITER:
            return qs.filter(owner=user)
        return qs.filter(verification_status="VERIFIED")

    def perform_update(self, serializer):
        company = self.get_object()
        user = self.request.user
        if user.role != Role.ADMIN and company.owner_id != user.id:
            self.permission_denied(self.request, message="You cannot modify this company.")
        serializer.save()

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        company = self.get_object()
        serializer = CompanyVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        company.verification_status = serializer.validated_data["verification_status"]
        company.verification_notes = serializer.validated_data.get("verification_notes", "")
        company.save(update_fields=["verification_status", "verification_notes", "updated_at"])
        create_notification(
            recipient=company.owner,
            title="Company verification updated",
            message=f"{company.company_name} is now {company.verification_status.lower()}.",
            notification_type="COMPANY",
        )
        return Response(CompanySerializer(company, context={"request": request}).data, status=status.HTTP_200_OK)
