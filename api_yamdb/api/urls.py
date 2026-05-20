from django.urls import path

from api.views import CommentViewSet, ReviewViewSet

review_list = ReviewViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
review_detail = ReviewViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy',
})

comment_list = CommentViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
comment_detail = CommentViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy',
})

urlpatterns = [
    path(
        'titles/<int:title_id>/reviews/',
        review_list,
        name='reviews-list',
    ),
    path(
        'titles/<int:title_id>/reviews/<int:pk>/',
        review_detail,
        name='reviews-detail',
    ),
    path(
        'titles/<int:title_id>/reviews/<int:review_id>/comments/',
        comment_list,
        name='comments-list',
    ),
    path(
        'titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
        comment_detail,
        name='comments-detail',
    ),
]
