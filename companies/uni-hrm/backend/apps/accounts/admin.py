from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from apps.accounts.models import OTPCode, Permission, Role, RolePermission, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin, ModelAdmin):
    """Админка пользователя с Unfold."""

    list_display = ["email", "first_name", "last_name", "is_verified", "is_active"]
    list_filter = ["is_active", "is_verified", "is_staff", "language"]
    search_fields = ["email", "first_name", "last_name", "phone"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Персональная информация"),
            {"fields": ("username", "first_name", "last_name", "phone", "avatar", "language")},
        ),
        (
            _("Статус"),
            {"fields": ("is_active", "is_staff", "is_superuser", "is_verified")},
        ),
        (
            _("Даты"),
            {"fields": ("last_login", "date_joined")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


class RolePermissionInline(TabularInline):
    model = RolePermission
    extra = 0
    autocomplete_fields = ["permission"]


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ["name", "code", "level"]
    list_filter = ["level"]
    search_fields = ["name", "code"]
    inlines = [RolePermissionInline]


@admin.register(Permission)
class PermissionAdmin(ModelAdmin):
    list_display = ["codename", "name", "module"]
    list_filter = ["module"]
    search_fields = ["codename", "name"]


@admin.register(OTPCode)
class OTPCodeAdmin(ModelAdmin):
    list_display = ["user", "code", "is_used", "expires_at", "attempts"]
    list_filter = ["is_used"]
    search_fields = ["user__email"]
    readonly_fields = ["code", "expires_at", "attempts"]
