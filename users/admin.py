from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User, RegistrationToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'last_name', 'first_name', 'role', 'tariff', 'group', 'is_active')
    list_filter = ('role', 'tariff', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'middle_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('middle_name', 'role', 'tariff', 'group')}),
    )


@admin.register(RegistrationToken)
class RegistrationTokenAdmin(admin.ModelAdmin):
    list_display = ('username', 'last_name', 'first_name', 'middle_name', 'created_by', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_by')
    search_fields = ('username', 'last_name', 'first_name')
    readonly_fields = ('token', 'created_at')
