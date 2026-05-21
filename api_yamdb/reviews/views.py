from django.db.models import Avg, Count
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

from .models import Category, Genre, Title
from .serializers import (
    CategorySerializer, GenreSerializer, 
    TitleReadSerializer, TitleCreateUpdateSerializer
)
from .permissions import IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet для категорий:
    - list (GET), create (POST), retrieve (GET), update (PUT), partial_update (PATCH), destroy (DELETE)
    - Удаление по slug (не по id)
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'  # Важно! Используем slug вместо id для lookup
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']


class GenreViewSet(viewsets.ModelViewSet):
    """
    ViewSet для жанров:
    - Аналогичен CategoryViewSet
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']


class TitleViewSet(viewsets.ModelViewSet):
    """
    ViewSet для произведений:
    - GET (list, retrieve) использует TitleReadSerializer (с подробной информацией)
    - POST, PUT, PATCH использует TitleWriteSerializer (для создания/обновления)
    - Поддерживает фильтрацию по category, genre, name, year
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    # Фильтрация по полям
    filterset_fields = ['category__slug', 'genre__slug', 'year']
    search_fields = ['title']  # Поиск по названию
    ordering_fields = ['title', 'year', 'rating']  # Сортировка
    ordering = ['-year']  # Сортировка по умолчанию (новые сначала)

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

        # Аннотируем средний рейтинг
        # Coalesce нужен, чтобы для произведений без отзывов был 0 или null
        # Если нет отзывов - рейтинг 0
        queryset = queryset.annotate(
            rating=Coalesce(Avg('reviews__score'), 0)
        )

        return queryset

    def get_serializer_class(self):
        """
        Выбираем сериализатор в зависимости от типа запроса
        """
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return TitleReadSerializer
        return TitleWriteSerializer

    def perform_create(self, serializer):
        """
        При создании произведения дополнительная логика не требуется,
        всё уже сделано в сериализаторе
        """
        serializer.save()
