import pytest
from django.contrib.auth import get_user_model

from apps.accounts.backends import RBACBackend
from apps.accounts.models import Permission, Role, RolePermission, UserRole

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123!",
    )


@pytest.fixture
def permission():
    return Permission.objects.create(
        codename="employees.view",
        name="View employees",
        module="employees",
    )


@pytest.fixture
def role(permission):
    role = Role.objects.create(
        name="HR Manager",
        code="hr_manager",
        level="global",
    )
    RolePermission.objects.create(role=role, permission=permission)
    return role


@pytest.mark.django_db
class TestRBAC:
    def test_assign_role_to_user(self, user, role):
        user_role = UserRole.objects.create(user=user, role=role)
        assert user_role.user == user
        assert user_role.role == role

    def test_rbac_backend_has_perm(self, user, role, permission):
        UserRole.objects.create(user=user, role=role)
        backend = RBACBackend()
        assert backend.has_perm(user, "employees.view") is True
        assert backend.has_perm(user, "employees.delete") is False

    def test_superuser_has_all_perms(self):
        superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="AdminPass123!",
        )
        backend = RBACBackend()
        assert backend.has_perm(superuser, "anything") is True

    def test_inactive_user_has_no_perms(self, user, role, permission):
        UserRole.objects.create(user=user, role=role)
        user.is_active = False
        user.save()
        backend = RBACBackend()
        assert backend.has_perm(user, "employees.view") is False

    def test_rbac_backend_authenticate(self):
        User.objects.create_user(
            username="authtest",
            email="auth@example.com",
            password="TestPass123!",
        )
        backend = RBACBackend()
        user = backend.authenticate(None, email="auth@example.com", password="TestPass123!")
        assert user is not None
        assert user.email == "auth@example.com"

    def test_rbac_backend_authenticate_wrong_password(self):
        User.objects.create_user(
            username="authtest2",
            email="auth2@example.com",
            password="TestPass123!",
        )
        backend = RBACBackend()
        user = backend.authenticate(None, email="auth2@example.com", password="wrong")
        assert user is None
