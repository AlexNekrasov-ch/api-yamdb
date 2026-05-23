from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet, TitleViewSet

# Создаём роутер
router = DefaultRouter()

# Регистрируем ViewSet'ы с их базовыми URL
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'titles', TitleViewSet, basename='title')

# Все эндпоинты, которые создаст роутер:
# /categories/ - GET (list), POST (create)
# /categories/{slug}/ - GET (retrieve), PUT (update), PATCH (partial_update), DELETE (destroy)
# /genres/ - аналогично
# /titles/ - аналогично (но с id вместо slug, так как у Title lookup_field не переопределён)
# /titles/{id}/ - GET, PUT, PATCH, DELETE

urlpatterns = [
    # Подключаем все URL из роутера
    path('', include(router.urls)),
]
