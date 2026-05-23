from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Кастомная модель пользователя
class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]

    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Уникальный идентификатор'
    )

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта'
    )

    bio = models.TextField(
        blank=True,
        verbose_name='Биография',
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=USER,
        verbose_name='Роль',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

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
class Category(models.Model):
    """Категории произведений (Фильмы, Книги, Музыка)"""
    name = models.CharField(
        max_length=256,
        unique=True,
        default='Без категории',
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Жанры произведений (Сказка, Рок, Артхаус)"""
    name = models.CharField(
        max_length=256,
        unique=True,
        default='Без жанра',
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг жанра'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведения, к которым пишут отзывы"""
    name = models.CharField(
        max_length=256,
        default='Без названия',
        verbose_name='Название произведения'
    )
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(2026)],
        default=2024,
        verbose_name='Год выпуска'
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
        through='TitleGenre',
        related_name='titles',
        verbose_name='Жанры'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')

    def __str__(self):
        return self.name


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
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_title_genre'
            )
        ]


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
            MinValueValidator(1, message='Оценка не может быть меньше 1'),
            MaxValueValidator(10, message='Оценка не может быть больше 10')
        ],
        help_text='Оцените произведение от 1 до 10'
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
                fields=['title', 'author'],
                name='unique_title_author_review'
            )
        ]

    def __str__(self):
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
        return f'Комментарий от {self.author.username}'
        'к отзыву {self.review.id}'
