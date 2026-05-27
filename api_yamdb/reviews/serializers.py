from rest_framework import serializers

from .models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий"""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения произведений (GET)"""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category'
        )

    def get_rating(self, obj):
        """Получение рейтинга из аннотированного поля или вычисление"""
        rating = getattr(obj, 'rating', None)
        if rating is not None:
            return round(rating, 1)
        return None


class TitleCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления произведений (POST, PUT, PATCH)"""
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
