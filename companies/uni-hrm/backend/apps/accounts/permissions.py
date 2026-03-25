from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    """Проверяет наличие RBAC-разрешения по codename."""

    def __init__(self, codename: str) -> None:
        self.codename = codename

    def has_permission(self, request, view) -> bool:
        if not request.user.is_authenticated:
            return False
        return request.user.has_perm(self.codename)


class HasRole(BasePermission):
    """Проверяет наличие роли по коду."""

    def __init__(self, role_code: str) -> None:
        self.role_code = role_code

    def has_permission(self, request, view) -> bool:
        if not request.user.is_authenticated:
            return False
        return request.user.user_roles.filter(role__code=self.role_code).exists()
