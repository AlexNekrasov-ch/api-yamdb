"""URL-маршруты для api (auth + users)."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', views.signup, name='signup'),
    path('auth/token/', views.token, name='token'),
    path('', include(router.urls)),
]
