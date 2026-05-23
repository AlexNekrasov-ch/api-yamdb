import secrets

from django.core.cache import cache
from django.core.mail import send_mail
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import User
from .permissions import IsAdmin
from .serializers import (
    SignupSerializer,
    TokenSerializer,
    UserMeSerializer,
    UserSerializer,
)


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

    code = secrets.token_hex(16)
    cache.set(f'confirmation_code_{username}', code, timeout=600)

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
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
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
