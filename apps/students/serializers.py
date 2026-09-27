from __future__ import annotations

from rest_framework import serializers

from apps.common.validators import validate_resume_file

from .models import Education, Skill, StudentProfile, StudentSkill


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ("id", "name")


class StudentSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source="skill", write_only=True, required=False
    )
    skill_name = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = StudentSkill
        fields = ("id", "skill", "skill_id", "skill_name", "proficiency")

    def validate(self, attrs):
        if not attrs.get("skill") and not attrs.get("skill_name"):
            raise serializers.ValidationError("Provide skill_id or skill_name.")
        return attrs

    def create(self, validated_data):
        name = validated_data.pop("skill_name", None)
        skill = validated_data.get("skill")
        if name and not skill:
            skill, _ = Skill.objects.get_or_create(name=name.strip())
            validated_data["skill"] = skill
        student = self.context["student"]
        obj, _created = StudentSkill.objects.update_or_create(
            student=student,
            skill=validated_data["skill"],
            defaults={"proficiency": validated_data.get("proficiency", "INTERMEDIATE")},
        )
        return obj


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = (
            "id",
            "institution",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "score",
        )


class StudentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    skills = StudentSkillSerializer(source="student_skills", many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)
    resume_url = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "registration_number",
            "phone",
            "date_of_birth",
            "gender",
            "department",
            "degree",
            "graduation_year",
            "cgpa",
            "backlogs",
            "github_url",
            "linkedin_url",
            "portfolio_url",
            "resume_url",
            "skills",
            "education",
        )
        read_only_fields = ("id", "email", "registration_number")

    def get_resume_url(self, obj):
        if not obj.resume:
            return ""
        request = self.context.get("request")
        url = obj.resume.url
        return request.build_absolute_uri(url) if request else url

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if user_data:
            for attr, value in user_data.items():
                setattr(instance.user, attr, value)
            instance.user.save()
        return super().update(instance, validated_data)


class ResumeUploadSerializer(serializers.Serializer):
    resume = serializers.FileField()

    def validate_resume(self, value):
        validate_resume_file(value)
        return value
