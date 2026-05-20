from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.permissions import IsAuthorOrModeratorOrAdmin
from api.serializers import CommentSerializer, ReviewSerializer
from reviews.models import Comment, Review


class TitleNestedMixin:
    """Фильтрация вложенных ресурсов по title_id из URL."""

    def get_title(self):
        from reviews.models import Title

        return get_object_or_404(Title, pk=self.kwargs['title_id'])


class ReviewViewSet(
    TitleNestedMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        if self.action == 'create':
            return (IsAuthenticated(),)
        return (IsAuthenticated(), IsAuthorOrModeratorOrAdmin())

    def get_queryset(self):
        return Review.objects.filter(title_id=self.kwargs['title_id'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['title'] = self.get_title()
        return context

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title(),
        )

    def create(self, request, *args, **kwargs):
        title = self.get_title()
        if Review.objects.filter(
            title=title,
            author=request.user,
        ).exists():
            return Response(
                {'non_field_errors': ['Вы уже оставляли отзыв на это произведение.']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)


class CommentViewSet(
    TitleNestedMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdmin,)
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (AllowAny(),)
        if self.action == 'create':
            return (IsAuthenticated(),)
        return (IsAuthenticated(), IsAuthorOrModeratorOrAdmin())

    def get_review(self):
        title = self.get_title()
        return get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title=title,
        )

    def get_queryset(self):
        return Comment.objects.filter(review=self.get_review())

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=self.get_review(),
        )
