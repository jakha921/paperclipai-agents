import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin_test", email="admin@test.com", password="testpass123"
    )


@pytest.mark.django_db
def test_leave_types_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/leaves/types/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_public_holidays_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/leaves/holidays/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_leave_requests_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/leaves/requests/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_leave_allocations_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/leaves/allocations/")
    assert response.status_code == 200
