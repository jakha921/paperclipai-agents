import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
    )


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "test@example.com", "password": "TestPass123!"},
        )
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "test@example.com"

    def test_login_wrong_password(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "test@example.com", "password": "wrong"},
        )
        assert response.status_code == 400

    def test_login_nonexistent_user(self, api_client):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "nonexist@example.com", "password": "pass"},
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestRegister:
    def test_register_success(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "new@example.com",
                "first_name": "New",
                "last_name": "User",
                "phone": "+998901234567",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
        )
        assert response.status_code == 201
        assert "access" in response.data
        assert User.objects.filter(email="new@example.com").exists()

    def test_register_password_mismatch(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "new@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "StrongPass123!",
                "password_confirm": "DifferentPass!",
            },
        )
        assert response.status_code == 400

    def test_register_duplicate_email(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "test@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "StrongPass123!",
                "password_confirm": "StrongPass123!",
            },
        )
        assert response.status_code == 400


@pytest.mark.django_db
class TestMe:
    def test_get_me(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == 200
        assert response.data["email"] == "test@example.com"

    def test_update_me(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.patch(
            "/api/v1/auth/me/",
            {"first_name": "Updated"},
        )
        assert response.status_code == 200
        assert response.data["first_name"] == "Updated"

    def test_me_unauthenticated(self, api_client):
        response = api_client.get("/api/v1/auth/me/")
        assert response.status_code == 401


@pytest.mark.django_db
class TestChangePassword:
    def test_change_password_success(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/v1/auth/change-password/",
            {
                "old_password": "TestPass123!",
                "new_password": "NewStrongPass456!",
            },
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.check_password("NewStrongPass456!")

    def test_change_password_wrong_old(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.post(
            "/api/v1/auth/change-password/",
            {
                "old_password": "wrong",
                "new_password": "NewStrongPass456!",
            },
        )
        assert response.status_code == 400
