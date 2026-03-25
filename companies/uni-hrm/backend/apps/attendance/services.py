from __future__ import annotations

import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from apps.attendance.models import TimeSheet, WorkSchedule
    from apps.departments.models import Employee


def calculate_worked_hours(
    check_in: datetime.time,
    check_out: datetime.time,
    schedule: WorkSchedule,
) -> tuple[Decimal, Decimal]:
    """Return (worked_hours, overtime_hours)."""
    if check_in is None or check_out is None:
        return Decimal("0.00"), Decimal("0.00")

    check_in_dt = datetime.datetime.combine(datetime.date.today(), check_in)
    check_out_dt = datetime.datetime.combine(datetime.date.today(), check_out)
    if check_out_dt <= check_in_dt:
        return Decimal("0.00"), Decimal("0.00")

    total_minutes = (check_out_dt - check_in_dt).seconds // 60

    # Subtract break time if within schedule
    if schedule.break_start and schedule.break_end:
        break_start_dt = datetime.datetime.combine(datetime.date.today(), schedule.break_start)
        break_end_dt = datetime.datetime.combine(datetime.date.today(), schedule.break_end)
        if check_in_dt <= break_start_dt and check_out_dt >= break_end_dt:
            break_minutes = (break_end_dt - break_start_dt).seconds // 60
            total_minutes -= break_minutes

    worked = Decimal(str(round(total_minutes / 60, 2)))

    # Calculate standard hours from schedule
    work_start_dt = datetime.datetime.combine(datetime.date.today(), schedule.work_start)
    work_end_dt = datetime.datetime.combine(datetime.date.today(), schedule.work_end)
    standard_minutes = (work_end_dt - work_start_dt).seconds // 60
    if schedule.break_start and schedule.break_end:
        break_start_dt = datetime.datetime.combine(datetime.date.today(), schedule.break_start)
        break_end_dt = datetime.datetime.combine(datetime.date.today(), schedule.break_end)
        standard_minutes -= (break_end_dt - break_start_dt).seconds // 60
    standard_hours = Decimal(str(round(standard_minutes / 60, 2)))

    overtime = max(Decimal("0.00"), worked - standard_hours)
    return worked, overtime


def generate_timesheet(employee: Employee, month: int, year: int) -> TimeSheet:
    """Aggregate AttendanceRecord for the month into a TimeSheet."""
    from django.db.models import Count, Q, Sum

    from apps.attendance.models import AttendanceRecord, TimeSheet

    records = AttendanceRecord.objects.filter(employee=employee, date__year=year, date__month=month)
    agg = records.aggregate(
        total_hours=Sum("worked_hours"),
        overtime_hours=Sum("overtime_hours"),
        days_present=Count("id", filter=Q(status=AttendanceRecord.Status.PRESENT)),
        days_absent=Count("id", filter=Q(status=AttendanceRecord.Status.ABSENT)),
        days_late=Count("id", filter=Q(status=AttendanceRecord.Status.LATE)),
        days_on_leave=Count("id", filter=Q(status=AttendanceRecord.Status.ON_LEAVE)),
    )

    timesheet, _ = TimeSheet.objects.update_or_create(
        employee=employee,
        month=month,
        year=year,
        defaults={
            "total_working_days": records.exclude(
                status__in=[AttendanceRecord.Status.HOLIDAY]
            ).count(),
            "days_present": agg["days_present"] or 0,
            "days_absent": agg["days_absent"] or 0,
            "days_late": agg["days_late"] or 0,
            "days_on_leave": agg["days_on_leave"] or 0,
            "total_hours": agg["total_hours"] or Decimal("0.00"),
            "overtime_hours": agg["overtime_hours"] or Decimal("0.00"),
        },
    )
    return timesheet


def get_auto_status(
    employee: Employee,
    date: datetime.date,
    check_in: datetime.time | None,
) -> str:
    """Determine attendance status: PRESENT/LATE/ABSENT/ON_LEAVE/HOLIDAY."""
    from apps.attendance.models import AttendanceRecord
    from apps.leaves.models import LeaveRequest, PublicHoliday

    # Check if holiday
    if PublicHoliday.objects.filter(date=date, is_working_day=False).exists():
        return AttendanceRecord.Status.HOLIDAY

    # Check if on approved leave
    if LeaveRequest.objects.filter(
        employee=employee,
        status=LeaveRequest.Status.APPROVED,
        start_date__lte=date,
        end_date__gte=date,
    ).exists():
        return AttendanceRecord.Status.ON_LEAVE

    if check_in is None:
        return AttendanceRecord.Status.ABSENT

    # Get employee schedule
    schedule_assignment = (
        employee.schedules.filter(effective_from__lte=date)
        .filter(models.Q(effective_to__isnull=True) | models.Q(effective_to__gte=date))
        .first()
    )

    if schedule_assignment:
        schedule = schedule_assignment.schedule
        # Late threshold: 15 minutes after work_start
        work_start_dt = datetime.datetime.combine(date, schedule.work_start)
        late_threshold = work_start_dt + datetime.timedelta(minutes=15)
        check_in_dt = datetime.datetime.combine(date, check_in)
        if check_in_dt > late_threshold:
            return AttendanceRecord.Status.LATE

    return AttendanceRecord.Status.PRESENT
