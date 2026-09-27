from __future__ import annotations

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from apps.notifications.models import Notification

logger = logging.getLogger("apps")


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_notification_email(self, notification_id: int) -> bool:
    try:
        notification = Notification.objects.select_related("recipient").get(pk=notification_id)
    except Notification.DoesNotExist:
        return False
    if not notification.recipient.email:
        return False
    try:
        send_mail(
            subject=f"[CampusHire] {notification.title}",
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.recipient.email],
            fail_silently=True,
        )
        return True
    except Exception as exc:
        logger.warning("Email delivery failed for notification %s: %s", notification_id, exc)
        raise self.retry(exc=exc)
