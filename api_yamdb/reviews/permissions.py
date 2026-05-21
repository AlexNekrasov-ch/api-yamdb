from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение на уровне запроса:
    - GET, HEAD, OPTIONS запросы доступны всем (включая анонимов)
    - Остальные методы (POST, PUT, PATCH, DELETE) - только администраторам
    """

    def has_permission(self, request, view):
        # Безопасные методы (только чтение) доступны всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для небезопасных методов проверяем,
        # является ли пользователь администратором
        # Анонимные пользователи не проходят эту проверку
        # (у них нет атрибута is_admin)
        return request.user.is_authenticated and request.user.is_admin
