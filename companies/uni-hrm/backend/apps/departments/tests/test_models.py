import pytest

from apps.departments.models import Department, Employee, Position


@pytest.fixture
def department(db):
    return Department.objects.create(
        code="TEST-DEPT",
        name={
            "ru": "Тестовый отдел",
            "uz": "Test bo'lim",
            "en": "Test Dept",
        },
        department_type=Department.DepartmentType.DEPARTMENT,
    )


@pytest.fixture
def position(db):
    return Position.objects.create(
        code="TEST-POS",
        name={
            "ru": "Тестовая должность",
            "uz": "Test lavozim",
            "en": "Test Position",
        },
        category=Position.Category.AUP,
    )


@pytest.mark.django_db
class TestDepartmentModel:
    def test_department_create(self, department):
        assert department.pk is not None
        assert department.code == "TEST-DEPT"

    def test_department_str(self, department):
        assert str(department) == "Тестовый отдел"

    def test_department_get_name(self, department):
        assert department.get_name("uz") == "Test bo'lim"
        assert department.get_name("en") == "Test Dept"

    def test_department_hierarchy(self, db, department):
        child = Department.objects.create(
            code="CHILD",
            name={"ru": "Дочерний"},
            department_type=Department.DepartmentType.DEPARTMENT,
            parent=department,
        )
        assert child.parent == department
        assert department.get_children().count() == 1


@pytest.mark.django_db
class TestPositionModel:
    def test_position_create(self, position):
        assert position.pk is not None
        assert position.category == Position.Category.AUP

    def test_position_str(self, position):
        assert str(position) == "Тестовая должность"


@pytest.mark.django_db
class TestEmployeeModel:
    def test_employee_create(self, db, department, position):
        emp = Employee.objects.create(
            department=department,
            position=position,
            first_name="Иван",
            last_name="Иванов",
            pinfl="31901011234501",
            passport_series="AA1234567",
            birth_date="1990-01-01",
            gender=Employee.Gender.MALE,
            nationality="Узбек",
            phone="+998901234567",
            hire_date="2024-01-01",
        )
        assert emp.pk is not None
        assert emp.full_name == "Иванов Иван"
        assert emp.status == Employee.Status.ACTIVE

    def test_soft_delete(self, db, department, position):
        emp = Employee.objects.create(
            department=department,
            position=position,
            first_name="Тест",
            last_name="Тестов",
            pinfl="31985051512345",
            passport_series="BB1234567",
            birth_date="1985-05-15",
            gender=Employee.Gender.MALE,
            nationality="Узбек",
            phone="+998901234568",
            hire_date="2024-01-01",
        )
        emp.soft_delete()
        emp.refresh_from_db()
        assert emp.is_deleted is True
        assert emp.deleted_at is not None
