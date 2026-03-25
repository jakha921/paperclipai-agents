import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import User
from apps.departments.models import Department, Position


@pytest.fixture
def api_client(db):
    user = User.objects.create_user(
        username="testuser", email="test@test.com", password="pass1234", is_verified=True
    )
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return client


@pytest.fixture
def department(db):
    return Department.objects.create(
        code="TEST",
        name={"ru": "Тест"},
        department_type=Department.DepartmentType.DEPARTMENT,
    )


@pytest.fixture
def position(db):
    return Position.objects.create(
        code="POS-TEST",
        name={"ru": "Тест-должность"},
        category="AUP",
    )


@pytest.mark.django_db
class TestDepartmentAPI:
    def test_list_departments(self, api_client, department):
        response = api_client.get("/api/v1/departments/")
        assert response.status_code == 200

    def test_create_department(self, api_client):
        data = {
            "code": "NEW-DEPT",
            "name": {"ru": "Новый отдел"},
            "department_type": "DEPARTMENT",
            "is_active": True,
        }
        response = api_client.post("/api/v1/departments/", data, format="json")
        assert response.status_code == 201

    def test_department_tree(self, api_client, department):
        response = api_client.get("/api/v1/departments/tree/")
        assert response.status_code == 200

    def test_org_chart(self, api_client, department):
        response = api_client.get("/api/v1/departments/org_chart/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestPositionAPI:
    def test_list_positions(self, api_client, position):
        response = api_client.get("/api/v1/positions/")
        assert response.status_code == 200

    def test_create_position(self, api_client):
        data = {
            "code": "NEW-POS",
            "name": {"ru": "Новая должность"},
            "category": "PPS",
            "is_academic": True,
        }
        response = api_client.post("/api/v1/positions/", data, format="json")
        assert response.status_code == 201
