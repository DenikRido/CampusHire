"""Role-based DRF permission classes. Backend always enforces these."""
from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.common.constants import Role


class IsAuthenticatedAndActive(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_active)


class IsStudent(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.role == Role.STUDENT)


class IsRecruiter(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.role == Role.RECRUITER)


class IsAdminRole(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.role == Role.ADMIN)


class IsRecruiterOrAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.role in {Role.RECRUITER, Role.ADMIN}
        )


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner attribute or admin role."""

    owner_field = "user"

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role == Role.ADMIN:
            return True
        owner = obj
        for attr in self.owner_field.split("."):
            owner = getattr(owner, attr, None)
            if owner is None:
                return False
        return owner == user


class ReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.method in SAFE_METHODS
