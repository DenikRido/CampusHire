"""In-app notifications are written synchronously; email is queued on Celery."""
from __future__ import annotations

import logging

from apps.common.constants import NotificationType
from apps.notifications.models import Notification

logger = logging.getLogger("apps")


def create_notification(
    *,
    recipient,
    title: str,
    message: str,
    notification_type: str = NotificationType.SYSTEM,
) -> Notification:
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
    )
    try:
        from apps.notifications.tasks import send_notification_email

        send_notification_email.delay(notification.id)
    except Exception:
        logger.info("Celery unavailable; skipped email for notification %s", notification.id)
    return notification
