from __future__ import annotations

from rest_framework import serializers

from apps.common.constants import CompanyVerificationStatus, Role

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)

    class Meta:
        model = Company
        fields = (
            "id",
            "company_name",
            "description",
            "website",
            "industry",
            "location",
            "verification_status",
            "verification_notes",
            "owner_email",
            "owner_name",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "verification_status",
            "verification_notes",
            "owner_email",
            "owner_name",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        user = self.context["request"].user
        if user.role != Role.RECRUITER:
            raise serializers.ValidationError("Only recruiters can create a company.")
        if Company.objects.filter(owner=user).exists():
            raise serializers.ValidationError("You already have a company profile.")
        return Company.objects.create(owner=user, **validated_data)


class CompanyVerificationSerializer(serializers.Serializer):
    verification_status = serializers.ChoiceField(choices=CompanyVerificationStatus.choices)
    verification_notes = serializers.CharField(required=False, allow_blank=True)
