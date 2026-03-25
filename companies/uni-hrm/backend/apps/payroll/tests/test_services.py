from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.departments.models import Department, Employee, Position
from apps.payroll.models import EmployeeSalary, TaxConfiguration
from apps.payroll.services import _get_working_days, calculate_payroll


class TestGetWorkingDays(TestCase):
    def test_january_2025(self):
        # Январь 2025: 23 рабочих дня
        assert _get_working_days(2025, 1) == 23

    def test_february_2025(self):
        # Февраль 2025: 20 рабочих дней
        assert _get_working_days(2025, 2) == 20


class TestCalculatePayroll(TestCase):
    def setUp(self):
        self.tax_config = TaxConfiguration.objects.create(
            year=2025,
            ndfl_rate=Decimal("0.12"),
            social_tax_rate=Decimal("0.12"),
            inps_employee_rate=Decimal("0.001"),
            inps_employer_rate=Decimal("0.001"),
            minimum_wage=Decimal("1155000"),
        )

        self.department = Department.objects.create(
            name={"ru": "Тестовый отдел"},
            code="TEST",
        )
        self.position = Position.objects.create(
            name={"ru": "Тестовая должность"},
            code="TEST_POS",
            category=Position.Category.AUP,
        )
        self.employee = Employee.objects.create(
            department=self.department,
            position=self.position,
            hire_date=date(2020, 1, 1),
            first_name="Иван",
            last_name="Иванов",
            pinfl="12345678901234",
            passport_series="AB1234567",
            birth_date=date(1990, 1, 1),
            gender=Employee.Gender.MALE,
            nationality="Узбекистан",
            phone="+998901234567",
        )

        self.salary = EmployeeSalary.objects.create(
            employee=self.employee,
            effective_from=date(2024, 1, 1),
            base_salary=Decimal("1000000"),
            is_active=True,
        )

    def test_calculate_creates_payroll(self):
        payroll = calculate_payroll(self.employee, 1, 2025)
        assert payroll is not None
        assert payroll.employee == self.employee
        assert payroll.month == 1
        assert payroll.year == 2025

    def test_ndfl_is_12_percent(self):
        payroll = calculate_payroll(self.employee, 1, 2025)
        expected_ndfl = (payroll.gross_salary * Decimal("0.12")).quantize(Decimal("0.01"))
        assert payroll.ndfl == expected_ndfl

    def test_net_equals_gross_minus_deductions(self):
        payroll = calculate_payroll(self.employee, 1, 2025)
        assert payroll.net_salary == payroll.gross_salary - payroll.total_deductions

    def test_no_tax_config_raises(self):
        with self.assertRaises(ValueError):
            calculate_payroll(self.employee, 1, 2030)

    def test_no_salary_raises(self):
        self.salary.is_active = False
        self.salary.save()
        with self.assertRaises(ValueError):
            calculate_payroll(self.employee, 1, 2025)
