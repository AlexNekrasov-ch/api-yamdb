import secrets

from django.core.cache import cache
from django.core.mail import send_mail
from django.db import models
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Comment, Genre, Review, Title, User
from .constants import CONFIRMATION_CODE_TIMEOUT, CONFIRMATION_TOKEN_BYTES
from .filters import TitleFilter
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignupSerializer,
                          TitleCreateUpdateSerializer, TitleReadSerializer,
                          TokenSerializer, UserMeSerializer, UserSerializer)


# Абстрактный базовый класс для опубликованных объектов
class PublishedAtModel(models.Model):
    pub_date = models.DateTimeField(
        'Дата и время создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True


# Абстрактный базовый класс для категорий и жанров
class SlugBasedViewSet(mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    """
    Абстрактный базовый ViewSet для моделей,
    использующих slug для идентификации.
    Поддерживает только GET (список), POST и DELETE.
    """
    permission_classes = (IsAdminOrReadOnly,)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_queryset(self):
        """Может быть переопределено в дочерних классах"""
        return super().get_queryset()

    def get_serializer_class(self):
        """Может быть переопределено в дочерних классах"""
        return super().get_serializer_class()


@api_view(['POST'])
def signup(request):
    """Регистрация пользователя и отправка confirmation_code на email."""
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']

    if not User.objects.filter(username=username, email=email).exists():
        if User.objects.filter(username=username).exists():
            return Response(
                {'username': [
                    'Пользователь с таким username уже существует.',
                ]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(email=email).exists():
            return Response(
                {'email': [
                    'Пользователь с таким email уже существует.',
                ]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        User.objects.create_user(
            username=username,
            email=email,
        )

    code = secrets.token_hex(CONFIRMATION_TOKEN_BYTES)
    cache.set(
        f'confirmation_code_{username}',
        code,
        timeout=CONFIRMATION_CODE_TIMEOUT
    )

    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {code}',
        None,
        [email],
        fail_silently=False,
    )

    return Response(
        {'email': email, 'username': username},
        status=status.HTTP_200_OK,
    )


@api_view(['POST'])
def token(request):
    """Обмен confirmation_code на JWT-токен."""
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {'username': ['Пользователь не найден.']},
            status=status.HTTP_404_NOT_FOUND,
        )

    cached_code = cache.get(f'confirmation_code_{username}')
    if cached_code != confirmation_code:
        return Response(
            {'confirmation_code': ['Неверный код подтверждения.']},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = AccessToken.for_user(user)
    return Response({'token': str(token)})


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для управления пользователями (только для admin)."""
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me',
    )
    def me(self, request):
        """Получение и редактирование профиля текущего пользователя."""
        user = request.user
        if request.method == 'GET':
            serializer = UserMeSerializer(user)
            return Response(serializer.data)
        serializer = UserMeSerializer(
            user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CategoryViewSet(SlugBasedViewSet):
    """
    ViewSet для категорий:
    - GET /categories/ — список категорий
    - POST /categories/ — создание категории (только admin)
    - DELETE /categories/{slug}/ — удаление категории (только admin)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(SlugBasedViewSet):
    """
    ViewSet для жанров:
    - GET /genres/ — список жанров
    - POST /genres/ — создание жанра (только admin)
    - DELETE /genres/{slug}/ — удаление жанра (только admin)
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для произведений (полный CRUD)
    """
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    )
    filterset_class = TitleFilter
    search_fields = ('name',)
    ordering_fields = ('name', 'year', 'rating')
    ordering = ('-year',)

    def get_queryset(self):
        """
        Оптимизированный queryset с аннотацией рейтинга
        """
        # Базовый queryset с оптимизацией
        queryset = (
            Title.objects
            .select_related('category')
            .prefetch_related('genre')
        )

        queryset = queryset.annotate(
            rating=models.Avg('reviews__score')
        )

        return queryset

    def get_serializer_class(self):
        """
        Выбираем сериализатор в зависимости от типа запроса
        """
        if self.action in ('create', 'update', 'partial_update'):
            return TitleCreateUpdateSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзывов (вложенный в titles)"""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return (
            Review.objects
            .filter(title_id=title_id)
            .select_related('author')
        )

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {'detail': 'Method PUT not allowed.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментариев (вложенный в reviews)"""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        return (
            Comment.objects
            .filter(review_id=review_id)
            .select_related('author')
        )

    def get_review(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        return get_object_or_404(Review, id=review_id, title_id=title_id)

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {'detail': 'Method PUT not allowed.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)
