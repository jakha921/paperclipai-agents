import pytest

from apps.departments.models import Department, Position


@pytest.fixture
def department(db):
    return Department.objects.create(
        code="RECRUIT-TEST-DEPT",
        name={"ru": "Тестовый отдел", "uz": "Test bo'lim", "en": "Test Dept"},
        department_type=Department.DepartmentType.DEPARTMENT,
    )


@pytest.fixture
def position(db):
    return Position.objects.create(
        code="RECRUIT-TEST-POS",
        name={"ru": "Тестовая должность", "uz": "Test lavozim", "en": "Test Position"},
        category=Position.Category.AUP,
    )
