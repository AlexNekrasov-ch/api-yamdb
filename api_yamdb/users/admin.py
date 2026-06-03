from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import User


class UserResource(resources.ModelResource):
    """Resource для импорта/экспорта пользователей."""

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'role',
            'bio', 'first_name', 'last_name'
        )
        import_id_fields = ('id',)
        skip_unchanged = True


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
        ('Personal info',
         {'fields': ('first_name', 'last_name', 'email', 'bio')}
         ),
        ('Permissions', {
            'fields': (
                'role', 'is_active', 'is_staff',
                'is_superuser', 'groups', 'user_permissions'
            ),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
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
