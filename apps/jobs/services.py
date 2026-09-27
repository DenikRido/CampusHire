"""Job workflow and student eligibility engine."""
from __future__ import annotations

from dataclasses import dataclass, field

from django.core.cache import cache
from django.db.models import QuerySet
from django.utils import timezone

from apps.common.constants import JOB_ADMIN_TRANSITIONS, JOB_OWNER_TRANSITIONS, JobStatus
from apps.jobs.models import Job
from apps.students.models import StudentProfile

CACHE_JOBS_KEY = "jobs:public:list:v1"


@dataclass
class EligibilityResult:
    eligible: bool
    reasons: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"eligible": self.eligible, "reasons": self.reasons}


def public_job_queryset() -> QuerySet[Job]:
    now = timezone.now()
    return (
        Job.objects.filter(status=JobStatus.ACTIVE, application_deadline__gte=now)
        .select_related("company")
        .prefetch_related("required_skills")
    )


def invalidate_job_cache() -> None:
    cache.delete(CACHE_JOBS_KEY)
    cache.delete_many(["dashboard:admin", "jobs:categories"])


def check_student_eligibility(student: StudentProfile, job: Job) -> EligibilityResult:
    """
    Return structured eligibility for a student against a job.

    Rules (all must pass):
    1. Job is ACTIVE
    2. Deadline has not passed
    3. Minimum CGPA
    4. Maximum backlogs
    5. Department is eligible (empty list = all)
    6. Degree is eligible (empty list = all)
    7. Graduation year matches when the job specifies one
    8. Required skills (if any are listed)
    9. Student has a resume
    10. Student has not already applied
    """
    reasons: list[str] = []
    now = timezone.now()

    if job.status != JobStatus.ACTIVE:
        reasons.append("Job is not currently active for applications.")
    if job.application_deadline < now:
        reasons.append("Application deadline has passed.")
    if not student.resume:
        reasons.append("A resume is required before you can apply.")
    if student.cgpa is None or student.cgpa < job.minimum_cgpa:
        reasons.append(f"Minimum CGPA required is {job.minimum_cgpa}.")
    if student.backlogs > job.maximum_backlogs:
        reasons.append(f"Maximum backlogs allowed is {job.maximum_backlogs}.")

    departments = job.eligible_departments or []
    if departments and student.department not in departments:
        reasons.append(f"Eligible departments: {', '.join(departments)}.")

    degrees = job.eligible_degrees or []
    if degrees and student.degree not in degrees:
        reasons.append(f"Eligible degrees: {', '.join(degrees)}.")

    if job.graduation_year and student.graduation_year != job.graduation_year:
        reasons.append(f"Eligible graduation year is {job.graduation_year}.")

    required = list(job.required_skills.all())
    if required:
        student_skill_ids = set(student.student_skills.values_list("skill_id", flat=True))
        missing = [skill.name for skill in required if skill.id not in student_skill_ids]
        for name in missing:
            reasons.append(f"Required skill: {name}")

    already = job.applications.filter(student=student).exists()
    if already:
        reasons.append("You have already applied to this job.")

    return EligibilityResult(eligible=not reasons, reasons=reasons)


def transition_job(job: Job, new_status: str, *, actor, reason: str = "") -> Job:
    current = job.status
    allowed: set[str] = set()
    if actor.role == "ADMIN":
        allowed = JOB_ADMIN_TRANSITIONS.get(current, set())
    else:
        allowed = JOB_OWNER_TRANSITIONS.get(current, set())
        if job.company.owner_id != actor.id and actor.role != "ADMIN":
            raise PermissionError("You cannot modify another recruiter's job.")

    if new_status not in allowed:
        raise ValueError(f"Cannot move job from {current} to {new_status}.")

    job.status = new_status
    if new_status == JobStatus.REJECTED:
        job.rejection_reason = reason
    elif new_status in {JobStatus.APPROVED, JobStatus.ACTIVE}:
        job.rejection_reason = ""
        if new_status == JobStatus.APPROVED:
            # Approving a still-open job makes it immediately visible to students.
            if job.application_deadline >= timezone.now():
                job.status = JobStatus.ACTIVE
    job.save(update_fields=["status", "rejection_reason", "updated_at"])
    invalidate_job_cache()
    return job
