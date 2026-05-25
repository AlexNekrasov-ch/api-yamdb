from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Category, Comment, Genre, Review, Title, TitleGenre, User


# --- Resources для импорта/экспорта ---
class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'role',
            'bio', 'first_name', 'last_name'
        )
        import_id_fields = ('id',)
        skip_unchanged = True


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


# --- Админ-классы ---
@admin.register(User)
class CustomUserAdmin(ImportExportModelAdmin, UserAdmin):
    resource_class = UserResource
    list_display = (
        'id', 'username', 'email', 'first_name',
        'last_name', 'role', 'is_staff'
    )
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'),
         {'fields': ('first_name', 'last_name', 'email', 'bio')}
         ),
        (_('Permissions'), {
            'fields': (
                'role', 'is_active', 'is_staff',
                'is_superuser', 'groups', 'user_permissions'
            ),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'role', 'first_name', 'last_name', 'bio'
            ),
        }),
    )


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


class TitleGenreInline(admin.TabularInline):
    """Inline-форма для управления связями жанров с произведением."""
    model = TitleGenre
    extra = 1
    autocomplete_fields = ['genre']
    verbose_name = 'Жанр'
    verbose_name_plural = 'Жанры'


@admin.register(Title)
class TitleAdmin(ImportExportModelAdmin):
    resource_class = TitleResource
    list_display = ('id', 'name', 'year', 'category', 'description')
    list_filter = ('year', 'category')
    search_fields = ('name', 'description')
    raw_id_fields = ('category',)
    inlines = [TitleGenreInline]


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
