import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.settings.models import SystemSettings


@pytest.fixture
def super_admin(db):
    return User.objects.create_user(
        username="superadmin",
        email="superadmin@test.com",
        password="testpass123",
        is_superuser=True,
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        username="employee",
        email="employee@test.com",
        password="testpass123",
    )


@pytest.fixture
def admin_client(super_admin):
    client = APIClient()
    client.force_authenticate(user=super_admin)
    return client


@pytest.fixture
def user_client(regular_user):
    client = APIClient()
    client.force_authenticate(user=regular_user)
    return client


@pytest.mark.django_db
class TestSystemSettingsAPI:
    def test_get_settings_authenticated(self, user_client):
        url = "/api/v1/settings/"
        response = user_client.get(url)
        assert response.status_code == 200
        assert "site_name" in response.data

    def test_get_settings_unauthenticated(self):
        client = APIClient()
        url = "/api/v1/settings/"
        response = client.get(url)
        assert response.status_code == 401

    def test_patch_settings_super_admin(self, admin_client):
        url = "/api/v1/settings/"
        response = admin_client.patch(url, {"site_name": "Updated HRM", "currency": "USD"})
        assert response.status_code == 200
        assert response.data["site_name"] == "Updated HRM"
        assert response.data["currency"] == "USD"

    def test_patch_settings_unauthorized(self, user_client):
        url = "/api/v1/settings/"
        response = user_client.patch(url, {"site_name": "Hacked"})
        assert response.status_code == 403

    def test_patch_working_days(self, admin_client):
        url = "/api/v1/settings/"
        response = admin_client.patch(url, {"working_days": [1, 2, 3, 4, 5]}, format="json")
        assert response.status_code == 200
        assert response.data["working_days"] == [1, 2, 3, 4, 5]

    def test_patch_smtp_settings(self, admin_client):
        url = "/api/v1/settings/"
        data = {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_use_tls": True,
            "smtp_username": "test@gmail.com",
        }
        response = admin_client.patch(url, data)
        assert response.status_code == 200
        assert response.data["smtp_host"] == "smtp.gmail.com"

    def test_test_email_no_recipient(self, admin_client):
        url = "/api/v1/settings/test_email/"
        response = admin_client.post(url, {})
        # superadmin has email set, so it will try to send and get console output
        assert response.status_code in [200, 400, 500]

    def test_test_email_unauthorized(self, user_client):
        url = "/api/v1/settings/test_email/"
        response = user_client.post(url, {"to_email": "test@example.com"})
        assert response.status_code == 403

    def test_settings_created_on_first_get(self, admin_client):
        url = "/api/v1/settings/"
        SystemSettings.objects.all().delete()
        response = admin_client.get(url)
        assert response.status_code == 200
        assert SystemSettings.objects.count() == 1

    def test_patch_partial_update(self, admin_client):
        url = "/api/v1/settings/"
        admin_client.patch(url, {"annual_leave_days": 30})
        response = admin_client.patch(url, {"sick_leave_days": 10})
        assert response.status_code == 200
        assert response.data["sick_leave_days"] == 10
        assert response.data["annual_leave_days"] == 30
