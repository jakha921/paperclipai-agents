from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj) -> bool:
        return hasattr(obj, "created_by") and obj.created_by == request.user


class IsHRManager(BasePermission):
    def has_permission(self, request, view) -> bool:
        return (
            request.user.is_authenticated
            and request.user.user_roles.filter(role__code="hr_manager").exists()
        )


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.is_superuser
