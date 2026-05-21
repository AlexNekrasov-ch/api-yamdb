from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

from .models import Category, Genre, Title, TitleGenre


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""

    name = serializers.CharField(source='title', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')
        # slug только для чтения при обновлении
        read_only_fields = ('slug',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""

    name = serializers.CharField(source='title', read_only=True)

    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')
        read_only_fields = ('slug',)


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений (GET)"""

    name = serializers.CharField(source='title')
    rating = serializers.SerializerMethodField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description',
                  'genre', 'category', 'is_published'
                  )

    def get_rating(self, obj):
        """Получение рейтинга из аннотированного поля или вычисление"""
        if hasattr(obj, 'rating'):
            return obj.rating
        # Если рейтинг не аннотирован, вычисляем
        rating = obj.reviews.aggregate(Avg('score'))['score__avg']
        return round(rating, 1) if rating else None


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления произведений (POST, PUT, PATCH)"""
    name = serializers.CharField(source='title')
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        """Проверка, что год не из будущего"""
        from django.utils import timezone
        current_year = timezone.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f'Год выпуска не может быть больше {current_year}'
            )
        return value

    def create(self, validated_data):
        """Создание произведения с жанрами"""
        genre_data = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        title.genre.set(genre_data)
        return title

    def update(self, instance, validated_data):
        """Обновление произведения с жанрами"""
        genre_data = validated_data.pop('genre', None)
        if genre_data is not None:
            instance.genre.set(genre_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        """При возврате данных используем сериализатор для чтения"""
        return TitleReadSerializer(instance).data
