from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from rest_framework import serializers

from api_yamdb.settings import MAX_LEN_EMAIL, MAX_LEN_USERNAME
from reviews.models import Category, Comment, Genre, Review, Title, User


class UsernameNotMeMixin:
    """Запрещает использование 'me' в качестве username."""

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" запрещено.'
            )
        return value


class SignupSerializer(UsernameNotMeMixin, serializers.Serializer):
    """Валидация данных при регистрации (email + username)."""
    email = serializers.EmailField(max_length=MAX_LEN_EMAIL)
    username = serializers.CharField(
        max_length=MAX_LEN_USERNAME,
        validators=[UnicodeUsernameValidator()],
    )


class TokenSerializer(serializers.Serializer):
    """Валидация username и confirmation_code для получения JWT."""
    username = serializers.CharField(max_length=MAX_LEN_USERNAME)
    confirmation_code = serializers.CharField()


class UserSerializer(UsernameNotMeMixin, serializers.ModelSerializer):
    """Сериализатор для полного управления пользователями (admin)."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'bio', 'role',
        )


class UserMeSerializer(UserSerializer):
    """Сериализатор для чтения/редактирования профиля."""
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


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
        # Обновляем стандартные поля через родительский метод
        instance = super().update(instance, validated_data)
        # ManyToMany поле обновляем отдельно
        if genre_data is not None:
            instance.genre.set(genre_data)

        return instance

    def to_representation(self, instance):
        """При возврате данных используем сериализатор для чтения"""
        return TitleReadSerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('pub_date',)

    def validate(self, data):
        """
        Проверка: пользователь может оставить только один отзыв на произведение
        """
        request = self.context.get('request')

        # Если не POST — пропускаем проверку
        if not request or request.method != 'POST':
            return data

        title_id = self.context['view'].kwargs.get('title_id')
        if request.user.reviews.filter(title_id=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев"""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('pub_date',)
