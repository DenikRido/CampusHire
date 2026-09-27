from __future__ import annotations

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsRecruiter
from apps.recruiters.models import RecruiterProfile

from .serializers import RecruiterProfileSerializer


class RecruiterMeView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsRecruiter]
    serializer_class = RecruiterProfileSerializer

    def get_object(self):
        profile, _ = RecruiterProfile.objects.get_or_create(user=self.request.user)
        return profile
