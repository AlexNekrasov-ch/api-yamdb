# users/models.py
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from api_yamdb.settings import MAX_LEN_EMAIL, MAX_LEN_USERNAME
from .constants import MAX_LEN_ROLE_NAME


class User(AbstractUser):
    """Кастомная модель пользователя с ролью и биографией."""
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    username = models.CharField(
        max_length=MAX_LEN_USERNAME,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        },
    )
    email = models.EmailField(
        max_length=MAX_LEN_EMAIL,
        unique=True,
        verbose_name='Email',
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография',
    )
    role = models.CharField(
        max_length=MAX_LEN_ROLE_NAME,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == self.MODERATOR
