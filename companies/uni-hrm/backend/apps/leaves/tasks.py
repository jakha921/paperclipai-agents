from __future__ import annotations

from datetime import date

try:
    from celery import shared_task
except ImportError:

    def shared_task(func):
        return func


@shared_task
def allocate_annual_leaves() -> dict:
    """Create/update LeaveAllocation for all active employees. Run on Jan 1."""
    from apps.departments.models import Employee
    from apps.leaves.models import LeaveAllocation, LeaveType

    year = date.today().year
    employees = Employee.objects.filter(status=Employee.Status.ACTIVE)
    created = 0
    for employee in employees:
        for leave_type in LeaveType.objects.all():
            category = employee.position.category if employee.position else None
            if not leave_type.applicable_categories:
                applicable = True
            else:
                applicable = category in leave_type.applicable_categories
            if applicable:
                _, is_created = LeaveAllocation.objects.get_or_create(
                    employee=employee,
                    leave_type=leave_type,
                    year=year,
                    defaults={"total_days": leave_type.days_per_year},
                )
                if is_created:
                    created += 1
    return {"created": created, "year": year}
