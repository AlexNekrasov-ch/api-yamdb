from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Кастомная модель пользователя
class User(AbstractUser):
    """Кастомная модель пользователя для гибкости"""
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]

    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


# Абстрактные модели
class CreatedAtModel(models.Model):
    """Абстрактная модель с датой создания"""
    created_at = models.DateTimeField(
        'Дата и время создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class PublishedModel(models.Model):
    """Абстрактная модель с флагом публикации"""
    is_published = models.BooleanField(
        'Опубликовано',
        default=True
    )

    class Meta:
        abstract = True


class TitledModel(models.Model):
    """Абстрактная модель с заголовком"""
    title = models.CharField(
        'Заголовок',
        max_length=256
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


# Основные модели проекта
class Category(PublishedModel, TitledModel):
    """Категории произведений (Фильмы, Книги, Музыка)"""
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        max_length=50,
        help_text='Уникальный slug для URL'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)

    def __str__(self):
        return self.title


class Genre(PublishedModel, TitledModel):
    """Жанры произведений (Сказка, Рок, Артхаус)"""
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        max_length=50,
        help_text='Уникальный slug для URL'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('title',)

    def __str__(self):
        return self.title


class Title(PublishedModel, TitledModel):
    """Произведения, к которым пишут отзывы"""
    description = models.TextField('Описание', blank=True)
    year = models.PositiveSmallIntegerField(
        'Год выпуска',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        related_name='titles',
        verbose_name='Жанры'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'title')

    def __str__(self):
        return self.title


class TitleGenre(models.Model):
    """Связующая модель для ManyToMany связи Title и Genre"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Жанр произведения'
        verbose_name_plural = 'Жанры произведений'
        unique_together = ('title', 'genre')

    def __str__(self):
        return f'{self.title} - {self.genre}'


class Review(CreatedAtModel):
    """Отзывы на произведения с оценкой"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    text = models.TextField('Текст отзыва')
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(1, message='Оценка не может быть меньше 1'),
            MaxValueValidator(10, message='Оценка не может быть больше 10')
        ],
        help_text='Оцените произведение от 1 до 10'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-created_at',)
        # Ограничение: один пользователь - один отзыв на произведение
        unique_together = ('title', 'author')

    def __str__(self):
        return f'Отзыв от {self.author} на {self.title} | Оценка: {self.score}'


class Comment(CreatedAtModel):
    """Комментарии к отзывам"""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    text = models.TextField('Текст комментария')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return f'Комментарий от {self.author} к отзыву {self.review.id}'
