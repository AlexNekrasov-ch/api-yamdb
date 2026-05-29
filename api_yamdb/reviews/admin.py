from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Category, Comment, Genre, Review, Title


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')
        import_id_fields = ('id',)


class GenreResource(resources.ModelResource):
    class Meta:
        model = Genre
        fields = ('id', 'name', 'slug')
        import_id_fields = ('id',)


class TitleResource(resources.ModelResource):
    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'category', 'description')
        import_id_fields = ('id',)


class ReviewResource(resources.ModelResource):
    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        import_id_fields = ('id',)


class CommentResource(resources.ModelResource):
    class Meta:
        model = Comment
        fields = ('id', 'review', 'text', 'author', 'pub_date')
        import_id_fields = ('id',)


@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    resource_class = CategoryResource
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Genre)
class GenreAdmin(ImportExportModelAdmin):
    resource_class = GenreResource
    list_display = ('id', 'name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(ImportExportModelAdmin):
    resource_class = TitleResource
    list_display = ('id', 'name', 'year', 'category', 'description')
    list_filter = ('year', 'category')
    search_fields = ('name', 'description')
    raw_id_fields = ('category',)
    filter_horizontal = ('genre',)


@admin.register(Review)
class ReviewAdmin(ImportExportModelAdmin):
    resource_class = ReviewResource
    list_display = ('id', 'title', 'author', 'score', 'pub_date')
    list_filter = ('score', 'pub_date', 'title')
    search_fields = ('text', 'author__username', 'title__name')
    raw_id_fields = ('title', 'author')
    readonly_fields = ('pub_date',)


@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin):
    resource_class = CommentResource
    list_display = ('id', 'review', 'author', 'pub_date')
    list_filter = ('pub_date', 'review__title')
    search_fields = ('text', 'author__username', 'review__title__name')
    raw_id_fields = ('review', 'author')
    readonly_fields = ('pub_date',)
