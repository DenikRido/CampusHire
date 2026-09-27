"""Shared enumerations used across CampusHire."""
from __future__ import annotations

from django.db import models


class Role(models.TextChoices):
    STUDENT = "STUDENT", "Student"
    RECRUITER = "RECRUITER", "Recruiter"
    ADMIN = "ADMIN", "Admin"


class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    OTHER = "OTHER", "Other"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY", "Prefer not to say"


class Department(models.TextChoices):
    CSE = "CSE", "Computer Science"
    IT = "IT", "Information Technology"
    ECE = "ECE", "Electronics and Communication"
    EEE = "EEE", "Electrical and Electronics"
    MECH = "MECH", "Mechanical"
    CIVIL = "CIVIL", "Civil"
    MBA = "MBA", "MBA"
    MCA = "MCA", "MCA"
    OTHER = "OTHER", "Other"


class Degree(models.TextChoices):
    BTECH = "BTECH", "B.Tech"
    BE = "BE", "B.E."
    MTECH = "MTECH", "M.Tech"
    MCA = "MCA", "MCA"
    MBA = "MBA", "MBA"
    BCA = "BCA", "BCA"
    BSC = "BSC", "B.Sc"
    MSC = "MSC", "M.Sc"


class SkillProficiency(models.TextChoices):
    BEGINNER = "BEGINNER", "Beginner"
    INTERMEDIATE = "INTERMEDIATE", "Intermediate"
    ADVANCED = "ADVANCED", "Advanced"
    EXPERT = "EXPERT", "Expert"


class CompanyVerificationStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    VERIFIED = "VERIFIED", "Verified"
    REJECTED = "REJECTED", "Rejected"


class EmploymentType(models.TextChoices):
    FULL_TIME = "FULL_TIME", "Full-time"
    INTERNSHIP = "INTERNSHIP", "Internship"
    CONTRACT = "CONTRACT", "Contract"
    PART_TIME = "PART_TIME", "Part-time"


class JobStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PENDING_APPROVAL = "PENDING_APPROVAL", "Pending approval"
    APPROVED = "APPROVED", "Approved"
    ACTIVE = "ACTIVE", "Active"
    CLOSED = "CLOSED", "Closed"
    REJECTED = "REJECTED", "Rejected"


class ApplicationStatus(models.TextChoices):
    APPLIED = "APPLIED", "Applied"
    UNDER_REVIEW = "UNDER_REVIEW", "Under review"
    SHORTLISTED = "SHORTLISTED", "Shortlisted"
    INTERVIEW_SCHEDULED = "INTERVIEW_SCHEDULED", "Interview scheduled"
    SELECTED = "SELECTED", "Selected"
    REJECTED = "REJECTED", "Rejected"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"


class InterviewMode(models.TextChoices):
    ONLINE = "ONLINE", "Online"
    OFFLINE = "OFFLINE", "On-site"
    HYBRID = "HYBRID", "Hybrid"


class InterviewResult(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PASSED = "PASSED", "Passed"
    FAILED = "FAILED", "Failed"
    NO_SHOW = "NO_SHOW", "No-show"


class NotificationType(models.TextChoices):
    APPLICATION_SUBMITTED = "APPLICATION_SUBMITTED", "Application submitted"
    APPLICATION_STATUS = "APPLICATION_STATUS", "Application status"
    INTERVIEW = "INTERVIEW", "Interview"
    SYSTEM = "SYSTEM", "System"
    COMPANY = "COMPANY", "Company"
    JOB = "JOB", "Job"


# Valid directed transitions for applications. Terminal states have empty sets.
APPLICATION_TRANSITIONS: dict[str, set[str]] = {
    ApplicationStatus.APPLIED: {
        ApplicationStatus.UNDER_REVIEW,
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
    },
    ApplicationStatus.UNDER_REVIEW: {
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
    },
    ApplicationStatus.SHORTLISTED: {
        ApplicationStatus.INTERVIEW_SCHEDULED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.SELECTED,
    },
    ApplicationStatus.INTERVIEW_SCHEDULED: {
        ApplicationStatus.SELECTED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.INTERVIEW_SCHEDULED,  # reschedule keeps the same status
    },
    ApplicationStatus.SELECTED: set(),
    ApplicationStatus.REJECTED: set(),
    ApplicationStatus.WITHDRAWN: set(),
}

WITHDRAWABLE_STATUSES = {
    ApplicationStatus.APPLIED,
    ApplicationStatus.UNDER_REVIEW,
}

INTERVIEW_ELIGIBLE_STATUSES = {
    ApplicationStatus.SHORTLISTED,
    ApplicationStatus.INTERVIEW_SCHEDULED,
}

JOB_PUBLIC_STATUSES = {JobStatus.ACTIVE}

# Recruiter may move a job through these owner-driven transitions.
JOB_OWNER_TRANSITIONS: dict[str, set[str]] = {
    JobStatus.DRAFT: {JobStatus.PENDING_APPROVAL},
    JobStatus.PENDING_APPROVAL: {JobStatus.DRAFT},
    JobStatus.APPROVED: {JobStatus.ACTIVE, JobStatus.CLOSED},
    JobStatus.ACTIVE: {JobStatus.CLOSED},
    JobStatus.CLOSED: {JobStatus.ACTIVE},
    JobStatus.REJECTED: {JobStatus.DRAFT, JobStatus.PENDING_APPROVAL},
}

JOB_ADMIN_TRANSITIONS: dict[str, set[str]] = {
    JobStatus.PENDING_APPROVAL: {JobStatus.APPROVED, JobStatus.REJECTED, JobStatus.ACTIVE},
    JobStatus.APPROVED: {JobStatus.ACTIVE, JobStatus.REJECTED, JobStatus.CLOSED},
    JobStatus.ACTIVE: {JobStatus.CLOSED, JobStatus.REJECTED},
    JobStatus.REJECTED: {JobStatus.PENDING_APPROVAL, JobStatus.APPROVED},
    JobStatus.CLOSED: {JobStatus.ACTIVE},
    JobStatus.DRAFT: {JobStatus.PENDING_APPROVAL, JobStatus.REJECTED},
}
