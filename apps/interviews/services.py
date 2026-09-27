from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.applications.models import Application
from apps.applications.services import change_application_status
from apps.common.constants import ApplicationStatus, INTERVIEW_ELIGIBLE_STATUSES, NotificationType
from apps.interviews.models import Interview
from apps.notifications.services import create_notification


def schedule_interview(
    *,
    application: Application,
    scheduled_at,
    mode: str,
    interviewer_name: str,
    meeting_link: str = "",
    location: str = "",
    notes: str = "",
    actor,
) -> Interview:
    if application.status not in INTERVIEW_ELIGIBLE_STATUSES:
        raise ValueError("Candidate must be shortlisted before an interview is scheduled.")
    if scheduled_at < timezone.now():
        raise ValueError("Interview date/time must be in the future.")
    if mode == "ONLINE" and not meeting_link:
        raise ValueError("A meeting link is required for online interviews.")

    with transaction.atomic():
        interview = Interview.objects.create(
            application=application,
            scheduled_at=scheduled_at,
            mode=mode,
            interviewer_name=interviewer_name,
            meeting_link=meeting_link,
            location=location,
            notes=notes,
        )
        if application.status != ApplicationStatus.INTERVIEW_SCHEDULED:
            change_application_status(
                application=application,
                new_status=ApplicationStatus.INTERVIEW_SCHEDULED,
                actor=actor,
                remarks="Interview scheduled",
            )
        create_notification(
            recipient=application.student.user,
            title="Interview scheduled",
            message=(
                f"An interview for {application.job.title} is scheduled at "
                f"{scheduled_at.strftime('%d %b %Y, %H:%M UTC')} ({mode.lower()})."
            ),
            notification_type=NotificationType.INTERVIEW,
        )
    return interview


def update_interview(*, interview: Interview, actor, **fields) -> Interview:
    scheduled_at = fields.get("scheduled_at", interview.scheduled_at)
    if scheduled_at and scheduled_at < timezone.now() and "scheduled_at" in fields:
        raise ValueError("Interview date/time must be in the future.")
    for key, value in fields.items():
        if value is not None and hasattr(interview, key):
            setattr(interview, key, value)
    interview.save()
    create_notification(
        recipient=interview.application.student.user,
        title="Interview updated",
        message=f"Your interview for {interview.application.job.title} was updated.",
        notification_type=NotificationType.INTERVIEW,
    )
    return interview
