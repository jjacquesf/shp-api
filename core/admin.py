"""
Django admin customization
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from django.utils.translation import gettext_lazy as _

from core import models

admin.site.unregister(Group)

class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users"""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )

class CustomGroupAdmin(GroupAdmin):
    fieldsets = (
        (None, {'fields': ('name', 'permissions')}),
        (_('Description'), {'fields': ('description',)}),
    )

admin.site.register(models.User, UserAdmin)
admin.site.register(models.CustomGroup, CustomGroupAdmin)
admin.site.register(models.Profile)
admin.site.register(models.Municipality)
admin.site.register(models.Institution)
admin.site.register(models.Dpe)
admin.site.register(models.Supplier)
admin.site.register(models.Department)
admin.site.register(models.StateOrg)
admin.site.register(models.SifUser)
admin.site.register(models.SianUser)