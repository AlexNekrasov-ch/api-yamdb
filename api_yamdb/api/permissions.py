from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешение только для администраторов (role=admin или is_superuser)."""

    def has_permission(self, request, view):
        """Проверяет, является ли пользователь администратором."""
        return (request.user.is_authenticated
                and (request.user.is_admin or request.user.is_staff))
