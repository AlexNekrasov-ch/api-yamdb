from rest_framework import permissions


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """Автор объекта, модератор, администратор или суперпользователь."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        if user.is_superuser or getattr(user, 'is_admin', False):
            return True
        if getattr(user, 'is_moderator', False):
            return True
        return obj.author == user
