from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .constants import (MAX_LEN_NAME, MAX_LEN_SLUG,
                        MAX_SCORE, MIN_SCORE, MIN_TITLE_YEAR)
from users.models import User


# Основные модели проекта
class Category(models.Model):
    """Категории произведений (Фильмы, Книги, Музыка)"""
    name = models.CharField(
        max_length=MAX_LEN_NAME,
        unique=True,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=MAX_LEN_SLUG,
        unique=True,
        verbose_name='Слаг категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        """Возвращает название категории."""
        return self.name


class Genre(models.Model):
    """Жанры произведений (Сказка, Рок, Артхаус)"""
    name = models.CharField(
        max_length=MAX_LEN_NAME,
        unique=True,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=MAX_LEN_SLUG,
        unique=True,
        verbose_name='Слаг жанра'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        """Возвращает название жанра."""
        return self.name


class Title(models.Model):
    """Произведения, к которым пишут отзывы"""
    name = models.CharField(
        max_length=MAX_LEN_NAME,
        verbose_name='Название произведения'
    )
    year = models.SmallIntegerField(
        validators=[
            MinValueValidator(MIN_TITLE_YEAR),
            MaxValueValidator(timezone.now().year)
        ],
        default=timezone.now().year,
        verbose_name='Год выпуска',
        db_index=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name='Жанры'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        default=''
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')

    def __str__(self):
        """Возвращает название произведения."""
        return self.name


class Review(models.Model):
    """Отзывы на произведения с оценкой"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(
                MIN_SCORE, message=f'Оценка не может быть меньше {MIN_SCORE}'
            ),
            MaxValueValidator(
                MAX_SCORE, message=f'Оценка не может быть больше {MAX_SCORE}'
            )
        ],
        help_text=f'Оцените произведение от {MIN_SCORE} до {MAX_SCORE}'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        null=True,
        blank=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        # Ограничение: один пользователь - один отзыв на произведение
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_title_author_review'
            )
        ]

    def __str__(self):
        """Возвращает строковое представление отзыва."""
        return f'Отзыв от {self.author.username} на {self.title.name}'


class Comment(models.Model):
    """Комментарии к отзывам"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        null=True,
        blank=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('pub_date',)

    def __str__(self):
        """Возвращает строковое представление комментария."""
        return (
            f'Комментарий от {self.author.username} '
            f'к отзыву {self.review.id}'
        )
