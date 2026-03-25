import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.departments.models import Department, Employee, Position

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="academic_test_user",
        email="academic@test.com",
        password="testpass123",
    )


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def department(db):
    return Department.objects.create(
        code="ACAD-TEST-DEPT",
        name={"ru": "Тестовая кафедра", "uz": "Test kafedra", "en": "Test Department"},
        department_type=Department.DepartmentType.DEPARTMENT,
    )


@pytest.fixture
def position(db):
    return Position.objects.create(
        code="ACAD-TEST-POS",
        name={"ru": "Тестовая должность", "uz": "Test lavozim", "en": "Test Position"},
        category=Position.Category.PPS,
        is_academic=True,
    )


@pytest.fixture
def employee(db, department, position):
    return Employee.objects.create(
        department=department,
        position=position,
        first_name="Тест",
        last_name="Тестов",
        pinfl="12345678901234",
        passport_series="AB1234567",
        birth_date="1990-01-01",
        gender=Employee.Gender.MALE,
        nationality="Узбекистан",
        phone="+998901234567",
        hire_date="2020-01-01",
    )
