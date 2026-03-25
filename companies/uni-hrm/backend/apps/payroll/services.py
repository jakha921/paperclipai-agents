from __future__ import annotations

import calendar
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.departments.models import Employee


def calculate_payroll(employee: Employee, month: int, year: int):
    """
    Расчёт зарплаты за месяц.

    1. Берёт активную EmployeeSalary
    2. Берёт TimeSheet данные
    3. Берёт TaxConfiguration для года
    4. Считает gross = salary * attendance_ratio + overtime
    5. Считает налоги (NDFL 12%, INPS 0.1%)
    6. net = gross - deductions
    """
    from apps.payroll.models import EmployeeSalary, Payroll, TaxConfiguration

    # 1. Получить налоговую конфигурацию
    try:
        tax_config = TaxConfiguration.objects.get(year=year)
    except TaxConfiguration.DoesNotExist:
        raise ValueError(f"TaxConfiguration for year {year} not found")

    # 2. Получить активную зарплату
    ref_date = date(year, month, 1)
    salary_obj = (
        EmployeeSalary.objects.filter(
            employee=employee,
            effective_from__lte=ref_date,
            is_active=True,
        )
        .order_by("-effective_from")
        .first()
    )
    if not salary_obj:
        raise ValueError(f"No active salary for employee {employee}")

    # 3. Посчитать рабочие дни в месяце (5 дней в неделю)
    working_days_in_month = _get_working_days(year, month)

    # 4. Данные посещаемости из TimeSheet
    days_worked, days_on_leave, days_absent, overtime_hours = _get_attendance_data(
        employee, month, year
    )

    # 5. Коэффициент посещаемости
    paid_days = days_worked + days_on_leave
    if working_days_in_month > 0:
        attendance_ratio = Decimal(str(paid_days)) / Decimal(str(working_days_in_month))
        attendance_ratio = min(attendance_ratio, Decimal("1"))
    else:
        attendance_ratio = Decimal("1")

    # 6. Начисления
    base_salary = salary_obj.base_salary
    academic_bonus = base_salary * salary_obj.academic_bonus_pct / Decimal("100")
    position_bonus = base_salary * salary_obj.position_bonus_pct / Decimal("100")
    seniority_bonus = base_salary * salary_obj.seniority_bonus_pct / Decimal("100")
    other_allowances = salary_obj.other_allowances

    gross_monthly = (
        base_salary + academic_bonus + position_bonus + seniority_bonus + other_allowances
    )

    # 7. Сверхурочные: overtime_hours * (hourly_rate * 1.5)
    if working_days_in_month > 0:
        hourly_rate = base_salary / (Decimal(str(working_days_in_month)) * Decimal("8"))
    else:
        hourly_rate = Decimal("0")
    overtime_payment = overtime_hours * hourly_rate * Decimal("1.5")

    # 8. Итого начислено
    gross_salary = gross_monthly * attendance_ratio + overtime_payment
    gross_salary = gross_salary.quantize(Decimal("0.01"))

    # 9. Налоги
    ndfl = (gross_salary * tax_config.ndfl_rate).quantize(Decimal("0.01"))
    inps_employee = (gross_salary * tax_config.inps_employee_rate).quantize(Decimal("0.01"))
    total_deductions = ndfl + inps_employee
    net_salary = gross_salary - total_deductions

    # 10. Обязательства работодателя
    employer_social_tax = (gross_salary * tax_config.social_tax_rate).quantize(Decimal("0.01"))
    employer_inps = (gross_salary * tax_config.inps_employer_rate).quantize(Decimal("0.01"))

    # 11. Создать или обновить Payroll
    payroll, created = Payroll.objects.update_or_create(
        employee=employee,
        month=month,
        year=year,
        defaults={
            "tax_config": tax_config,
            "base_salary": base_salary,
            "academic_bonus": academic_bonus.quantize(Decimal("0.01")),
            "position_bonus": position_bonus.quantize(Decimal("0.01")),
            "seniority_bonus": seniority_bonus.quantize(Decimal("0.01")),
            "other_allowances": other_allowances,
            "working_days_in_month": working_days_in_month,
            "days_worked": days_worked,
            "days_on_leave": days_on_leave,
            "days_absent": days_absent,
            "overtime_hours": overtime_hours,
            "attendance_ratio": attendance_ratio.quantize(Decimal("0.0001")),
            "overtime_payment": overtime_payment.quantize(Decimal("0.01")),
            "gross_salary": gross_salary,
            "ndfl": ndfl,
            "inps_employee": inps_employee,
            "other_deductions": Decimal("0"),
            "total_deductions": total_deductions,
            "net_salary": net_salary.quantize(Decimal("0.01")),
            "employer_social_tax": employer_social_tax,
            "employer_inps": employer_inps,
            "status": Payroll.Status.CALCULATED,
        },
    )

    return payroll


def _get_working_days(year: int, month: int) -> int:
    """Считает рабочие дни (Пн-Пт) в месяце."""
    count = 0
    _, days_in_month = calendar.monthrange(year, month)
    for day in range(1, days_in_month + 1):
        weekday = calendar.weekday(year, month, day)
        if weekday < 5:  # 0=Mon, 4=Fri
            count += 1
    return count


def _get_attendance_data(
    employee: Employee, month: int, year: int
) -> tuple[int, int, int, Decimal]:
    """Получает данные посещаемости из TimeSheet или возвращает defaults."""
    try:
        from apps.attendance.models import TimeSheet

        timesheet = TimeSheet.objects.filter(
            employee=employee,
            month=month,
            year=year,
        ).first()

        if timesheet:
            days_worked = timesheet.days_present
            days_on_leave = timesheet.days_on_leave
            days_absent = timesheet.days_absent
            overtime_hours = timesheet.overtime_hours
            return days_worked, days_on_leave, days_absent, overtime_hours
    except (ImportError, LookupError, AttributeError):
        pass

    # Если TimeSheet недоступен, возвращаем дефолты
    working_days = _get_working_days(year, month)
    return working_days, 0, 0, Decimal("0")
