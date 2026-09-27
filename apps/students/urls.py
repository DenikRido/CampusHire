from django.urls import path

from .views import MeSkillDeleteView, MeSkillsView, MeStudentView, ResumeUploadView

urlpatterns = [
    path("me/", MeStudentView.as_view(), name="api-student-me"),
    path("me/skills/", MeSkillsView.as_view(), name="api-student-skills"),
    path("me/skills/<int:pk>/", MeSkillDeleteView.as_view(), name="api-student-skill-delete"),
    path("me/resume/", ResumeUploadView.as_view(), name="api-student-resume"),
]
