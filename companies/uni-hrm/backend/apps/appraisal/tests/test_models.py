from decimal import Decimal

import pytest

from apps.appraisal.models import (
    AppraisalCycle,
    AppraisalScore,
    EmployeeAppraisal,
    KPIIndicator,
    TrainingProgram,
)
from apps.appraisal.services import calculate_weighted_score, get_rating_label


@pytest.mark.django_db
def test_appraisal_cycle_str():
    cycle = AppraisalCycle(name="2025 H1", start_date="2025-01-01", end_date="2025-06-30")
    assert str(cycle) == "2025 H1"


@pytest.mark.django_db
def test_kpi_indicator_str():
    kpi = KPIIndicator(
        name={"ru": "Публикации", "en": "Publications"},
        category="academic",
        weight=Decimal("30.00"),
        max_score=10,
    )
    assert str(kpi) == "Публикации"


@pytest.mark.django_db
def test_training_program_str():
    program = TrainingProgram(
        name={"ru": "Python курс"},
        training_type="online",
    )
    assert str(program) == "Python курс"


@pytest.mark.django_db
def test_get_rating_label():
    assert get_rating_label(Decimal("9.0")) == "Отлично"
    assert get_rating_label(Decimal("8.5")) == "Отлично"
    assert get_rating_label(Decimal("7.5")) == "Хорошо"
    assert get_rating_label(Decimal("7.0")) == "Хорошо"
    assert get_rating_label(Decimal("6.0")) == "Удовлетворительно"
    assert get_rating_label(Decimal("5.0")) == "Удовлетворительно"
    assert get_rating_label(Decimal("4.9")) == "Неудовлетворительно"
    assert get_rating_label(Decimal("0.0")) == "Неудовлетворительно"


@pytest.mark.django_db
def test_calculate_weighted_score_empty(department_and_employee):
    department, employee = department_and_employee
    cycle = AppraisalCycle.objects.create(
        name="Test Cycle", start_date="2025-01-01", end_date="2025-06-30"
    )
    appraisal = EmployeeAppraisal.objects.create(cycle=cycle, employee=employee)
    assert calculate_weighted_score(appraisal) == Decimal("0.00")


@pytest.mark.django_db
def test_calculate_weighted_score_with_scores(department_and_employee):
    department, employee = department_and_employee
    cycle = AppraisalCycle.objects.create(
        name="Test Cycle", start_date="2025-01-01", end_date="2025-06-30"
    )
    appraisal = EmployeeAppraisal.objects.create(cycle=cycle, employee=employee)

    kpi1 = KPIIndicator.objects.create(
        name={"ru": "KPI 1"}, category="academic", weight=Decimal("50.00"), max_score=10
    )
    kpi2 = KPIIndicator.objects.create(
        name={"ru": "KPI 2"}, category="research", weight=Decimal("50.00"), max_score=10
    )

    AppraisalScore.objects.create(appraisal=appraisal, kpi=kpi1, self_score=8, manager_score=10)
    AppraisalScore.objects.create(appraisal=appraisal, kpi=kpi2, final_score=Decimal("7.00"))

    result = calculate_weighted_score(appraisal)
    # kpi1: avg(8,10)=9, normalized=9/10*10=9, weighted=9*50=450
    # kpi2: final=7, normalized=7/10*10=7, weighted=7*50=350
    # total=800/100=8.00
    assert result == Decimal("8.00")


@pytest.fixture
def department_and_employee(db):
    from apps.departments.models import Department, Employee, Position

    dept = Department.objects.create(
        name={"ru": "Тестовый отдел"},
        code="TEST_APPR",
        department_type="DEPARTMENT",
    )
    position = Position.objects.create(
        name={"ru": "Тестовая должность"},
        code="TEST_POS_APPR",
        category="PPS",
    )
    employee = Employee.objects.create(
        first_name="Тест",
        last_name="Тестов",
        department=dept,
        position=position,
        hire_date="2020-01-01",
        pinfl="12345678901234",
        passport_series="AA1234567",
        birth_date="1990-01-01",
        gender="MALE",
        nationality="Узбек",
        phone="+998901234567",
    )
    return dept, employee
