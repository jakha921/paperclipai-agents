from __future__ import annotations

import datetime

try:
    from celery import shared_task
except ImportError:

    def shared_task(func):
        return func


@shared_task
def generate_monthly_timesheets(month: int | None = None, year: int | None = None) -> dict:
    """Generate TimeSheet for all active employees for the given month."""
    from apps.attendance.services import generate_timesheet
    from apps.departments.models import Employee

    today = datetime.date.today()
    if month is None or year is None:
        # Previous month
        first_of_month = today.replace(day=1)
        prev_month = first_of_month - datetime.timedelta(days=1)
        month = prev_month.month
        year = prev_month.year

    employees = Employee.objects.filter(status=Employee.Status.ACTIVE)
    count = 0
    for employee in employees:
        generate_timesheet(employee, month, year)
        count += 1

    return {"processed": count, "month": month, "year": year}
