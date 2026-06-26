from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'name', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active')
    ordering = ('-created_at',)
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'name', 'is_approved')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'name', 'email', 'is_approved')}),
    )


admin.site.register(User, CustomUserAdmin)
