"""
Custom DRF permissions for Tasks.

IsOwnerOrReadOnly:
  - Any request using a safe HTTP method (GET, HEAD, OPTIONS) is allowed.
  - Write methods (POST, PUT, PATCH, DELETE) require the request user to be
    the owner of the task object.

IsAdminRoleOrOwner:
  - Users with role='admin' can read/write any task.
  - Regular users can only read/write their own tasks.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """Object-level permission: only the task owner can modify or delete it."""

    message = "You do not have permission to modify this task."

    def has_object_permission(self, request, view, obj):
        # Read-only methods are always allowed (list/retrieve are handled at view level)
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAdminRoleOrOwner(BasePermission):
    """
    Admins (role='admin') bypass ownership — they can access any task.
    Regular users are restricted to their own tasks.
    """

    message = "You do not have permission to access this task."

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_role:
            return True
        return obj.user == request.user
