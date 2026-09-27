from __future__ import annotations

from apps.common.constants import Role


def ui_defaults(request):
    user = getattr(request, "user", None)
    unread = 0
    if user is not None and user.is_authenticated:
        try:
            unread = user.notifications.filter(is_read=False).count()
        except Exception:
            unread = 0
    return {
        "Role": Role,
        "unread_notification_count": unread,
    }
