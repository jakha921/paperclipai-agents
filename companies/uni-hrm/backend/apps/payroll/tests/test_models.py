from decimal import Decimal

from django.test import TestCase

from apps.payroll.models import EmployeeSalary, TaxConfiguration


class TestTaxConfiguration(TestCase):
    def test_str(self):
        tc = TaxConfiguration(year=2025)
        assert str(tc) == "Tax Config 2025"

    def test_defaults(self):
        tc = TaxConfiguration.objects.create(year=2025)
        assert tc.ndfl_rate == Decimal("0.12")
        assert tc.inps_employee_rate == Decimal("0.001")
        assert tc.minimum_wage == Decimal("1155000")


class TestEmployeeSalary(TestCase):
    def test_gross_monthly_no_bonuses(self):
        salary = EmployeeSalary(
            base_salary=Decimal("1000000"),
            academic_bonus_pct=Decimal("0"),
            position_bonus_pct=Decimal("0"),
            seniority_bonus_pct=Decimal("0"),
            other_allowances=Decimal("0"),
        )
        assert salary.gross_monthly == Decimal("1000000")

    def test_gross_monthly_with_bonuses(self):
        salary = EmployeeSalary(
            base_salary=Decimal("1000000"),
            academic_bonus_pct=Decimal("10"),
            position_bonus_pct=Decimal("5"),
            seniority_bonus_pct=Decimal("5"),
            other_allowances=Decimal("50000"),
        )
        # bonuses = 1000000 * 20% = 200000
        # gross = 1000000 + 200000 + 50000 = 1250000
        assert salary.gross_monthly == Decimal("1250000")
