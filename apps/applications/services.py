"""Application creation, withdrawals, and validated status transitions."""
from __future__ import annotations

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.applications.models import Application, ApplicationStatusHistory
from apps.common.constants import (
    APPLICATION_TRANSITIONS,
    ApplicationStatus,
    NotificationType,
    WITHDRAWABLE_STATUSES,
)
from apps.common.exceptions import ConflictError, EligibilityError
from apps.jobs.models import Job
from apps.jobs.services import check_student_eligibility
from apps.notifications.services import create_notification
from apps.students.models import StudentProfile


def apply_to_job(*, student: StudentProfile, job: Job, cover_letter: str = "") -> Application:
    result = check_student_eligibility(student, job)
    if not result.eligible:
        raise EligibilityError(reasons=result.reasons)

    try:
        with transaction.atomic():
            application = Application.objects.create(
                student=student,
                job=job,
                cover_letter=cover_letter,
                status=ApplicationStatus.APPLIED,
            )
            if student.resume:
                application.resume_snapshot = student.resume
                application.save(update_fields=["resume_snapshot"])
            ApplicationStatusHistory.objects.create(
                application=application,
                old_status="",
                new_status=ApplicationStatus.APPLIED,
                changed_by=student.user,
                remarks="Application submitted",
            )
            create_notification(
                recipient=student.user,
                title="Application submitted",
                message=f"Your application for {job.title} at {job.company.company_name} was submitted.",
                notification_type=NotificationType.APPLICATION_SUBMITTED,
            )
            create_notification(
                recipient=job.company.owner,
                title="New application received",
                message=(
                    f"{student.user.full_name} applied for {job.title} "
                    f"({student.registration_number})."
                ),
                notification_type=NotificationType.APPLICATION_SUBMITTED,
            )
    except IntegrityError as exc:
        raise ConflictError("You have already applied to this job.") from exc
    return application


def change_application_status(
    *,
    application: Application,
    new_status: str,
    actor,
    remarks: str = "",
) -> Application:
    current = application.status
    allowed = APPLICATION_TRANSITIONS.get(current, set())
    if new_status not in allowed:
        raise ValueError(f"Cannot change status from {current} to {new_status}.")

    with transaction.atomic():
        application.status = new_status
        application.save(update_fields=["status", "updated_at"])
        ApplicationStatusHistory.objects.create(
            application=application,
            old_status=current,
            new_status=new_status,
            changed_by=actor,
            remarks=remarks,
        )
        if new_status in {
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.SELECTED,
            ApplicationStatus.INTERVIEW_SCHEDULED,
        }:
            verb = new_status.replace("_", " ").title()
            create_notification(
                recipient=application.student.user,
                title=f"Application {verb.lower()}",
                message=(
                    f"Your application for {application.job.title} is now {verb.lower()}."
                    + (f" {remarks}" if remarks else "")
                ),
                notification_type=NotificationType.APPLICATION_STATUS,
            )
    return application


def withdraw_application(*, application: Application, actor) -> Application:
    if application.status not in WITHDRAWABLE_STATUSES:
        raise ValueError("This application can no longer be withdrawn.")
    if application.student.user_id != actor.id and actor.role != "ADMIN":
        raise PermissionError("You can only withdraw your own application.")
    return change_application_status(
        application=application,
        new_status=ApplicationStatus.WITHDRAWN,
        actor=actor,
        remarks="Withdrawn by student",
    )


def recruiter_owns_application(user, application: Application) -> bool:
    if user.role == "ADMIN":
        return True
    return application.job.company.owner_id == user.id
