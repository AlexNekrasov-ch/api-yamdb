from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers

from reviews.models import User


class UsernameNotMeMixin:
    """Запрещает использование 'me' в качестве username."""

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" запрещено.'
            )
        return value


class SignupSerializer(UsernameNotMeMixin, serializers.Serializer):
    """Валидация данных при регистрации (email + username)."""
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(
        max_length=150,
        validators=[UnicodeUsernameValidator()],
    )


class TokenSerializer(serializers.Serializer):
    """Валидация username и confirmation_code для получения JWT."""
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class UserSerializer(UsernameNotMeMixin, serializers.ModelSerializer):
    """Сериализатор для полного управления пользователями (admin)."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'bio', 'role',
        )


class UserMeSerializer(UserSerializer):
    """Сериализатор для чтения/редактирования профиля."""
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
