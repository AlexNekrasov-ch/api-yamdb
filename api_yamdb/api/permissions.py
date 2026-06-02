from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Разрешение только для администраторов."""

    def has_permission(self, request, view):
        """Проверяет, является ли пользователь администратором."""
        return (request.user.is_authenticated
                and request.user.is_admin)


class IsAuthenticatedAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на уровне запроса:
    - GET, HEAD, OPTIONS запросы доступны всем (включая анонимов)
    - Остальные методы (POST, PUT, PATCH, DELETE) - только администраторам
    """

    def has_permission(self, request, view):
        """Только админы могут изменять данные."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return (request.user.is_authenticated
                and (
                    request.user.is_admin or request.user.is_superuser)
                )


class SafeOrAuthenticatedAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """Разрешение: автор, модератор, админ могут изменять/удалять"""
    def has_permission(self, request, view):
        """Для POST нужна аутентификация."""
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        """Изменять/удалять может автор, модератор или админ."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
            or request.user.is_superuser
        )
