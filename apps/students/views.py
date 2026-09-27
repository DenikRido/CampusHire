from __future__ import annotations

from rest_framework import generics, parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsStudent

from .models import StudentProfile, StudentSkill
from .serializers import (
    ResumeUploadSerializer,
    StudentProfileSerializer,
    StudentSkillSerializer,
)


def _profile(user) -> StudentProfile:
    profile, _ = StudentProfile.objects.get_or_create(
        user=user,
        defaults={
            "registration_number": f"TMP{user.id:06d}",
            "department": "CSE",
            "degree": "BTECH",
            "graduation_year": 2026,
            "cgpa": 0,
        },
    )
    return profile


class MeStudentView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsStudent]
    serializer_class = StudentProfileSerializer

    def get_object(self):
        return (
            StudentProfile.objects.select_related("user")
            .prefetch_related("student_skills__skill", "education")
            .get(pk=_profile(self.request.user).pk)
        )


class MeSkillsView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        profile = _profile(request.user)
        skills = profile.student_skills.select_related("skill")
        return Response(StudentSkillSerializer(skills, many=True).data)

    def post(self, request):
        profile = _profile(request.user)
        serializer = StudentSkillSerializer(data=request.data, context={"student": profile})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MeSkillDeleteView(APIView):
    permission_classes = [IsStudent]

    def delete(self, request, pk: int):
        profile = _profile(request.user)
        deleted, _ = StudentSkill.objects.filter(pk=pk, student=profile).delete()
        if not deleted:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResumeUploadView(APIView):
    permission_classes = [IsStudent]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        serializer = ResumeUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = _profile(request.user)
        if profile.resume:
            profile.resume.delete(save=False)
        profile.resume = serializer.validated_data["resume"]
        profile.save(update_fields=["resume", "updated_at"])
        return Response({"detail": "Resume uploaded.", "resume_url": profile.resume.url})
