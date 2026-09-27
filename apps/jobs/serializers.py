from __future__ import annotations

from rest_framework import serializers

from apps.students.serializers import SkillSerializer

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.company_name", read_only=True)
    company_id = serializers.IntegerField(source="company.id", read_only=True)
    required_skills = SkillSerializer(many=True, read_only=True)
    required_skill_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    salary_range = serializers.CharField(read_only=True)
    is_open_for_applications = serializers.BooleanField(read_only=True)

    class Meta:
        model = Job
        fields = (
            "id",
            "company_id",
            "company_name",
            "title",
            "description",
            "employment_type",
            "location",
            "minimum_cgpa",
            "maximum_backlogs",
            "eligible_departments",
            "eligible_degrees",
            "graduation_year",
            "salary_min",
            "salary_max",
            "salary_range",
            "required_skills",
            "required_skill_ids",
            "application_deadline",
            "status",
            "rejection_reason",
            "is_open_for_applications",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "rejection_reason", "created_at", "updated_at")

    def create(self, validated_data):
        skill_ids = validated_data.pop("required_skill_ids", [])
        job = Job.objects.create(**validated_data)
        if skill_ids:
            job.required_skills.set(skill_ids)
        return job

    def update(self, instance, validated_data):
        skill_ids = validated_data.pop("required_skill_ids", None)
        job = super().update(instance, validated_data)
        if skill_ids is not None:
            job.required_skills.set(skill_ids)
        return job


class JobStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    reason = serializers.CharField(required=False, allow_blank=True)
