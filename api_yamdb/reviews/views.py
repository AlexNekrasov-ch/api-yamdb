from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets

from .filters import TitleFilter
from .models import Category, Genre, Title
from .permissions import IsAdminOrReadOnly
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleCreateUpdateSerializer, TitleReadSerializer)


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
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ('name',)


    def get_queryset(self):
        """Может быть переопределено в дочерних классах"""
        return super().get_queryset()

    def get_serializer_class(self):
        """Может быть переопределено в дочерних классах"""
        return super().get_serializer_class()


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
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]
    filterset_class = TitleFilter
    search_fields = ['name']
    ordering_fields = ['name', 'year', 'rating']
    ordering = ['-year']

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
            rating=Avg('reviews__score')
        )

        return queryset

    def get_serializer_class(self):
        """
        Выбираем сериализатор в зависимости от типа запроса
        """
        if self.action in ('create', 'update', 'partial_update'):
            return TitleCreateUpdateSerializer
        return TitleReadSerializer
