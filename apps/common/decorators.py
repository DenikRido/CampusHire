from __future__ import annotations

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from apps.common.constants import Role


def role_required(*roles: str):
    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles and not (
                request.user.role == Role.ADMIN and Role.ADMIN in roles
            ):
                if request.user.role not in roles:
                    raise PermissionDenied("You do not have access to this page.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


student_required = role_required(Role.STUDENT)
recruiter_required = role_required(Role.RECRUITER)
admin_required = role_required(Role.ADMIN)
