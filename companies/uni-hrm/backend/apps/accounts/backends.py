from django.contrib.auth.backends import ModelBackend

from apps.accounts.models import User


class RBACBackend(ModelBackend):
    """Бэкенд аутентификации с RBAC через UserRole → Role → Permission."""

    def has_perm(self, user_obj: User, perm: str, obj=None) -> bool:
        if not user_obj.is_active:
            return False

        if user_obj.is_superuser:
            return True

        # Проверяем разрешение через цепочку UserRole → Role → Permission
        return user_obj.user_roles.filter(
            role__role_permissions__permission__codename=perm,
        ).exists()
