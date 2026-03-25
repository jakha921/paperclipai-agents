import datetime
from decimal import Decimal

from apps.attendance.models import WorkSchedule
from apps.attendance.services import calculate_worked_hours


def test_calculate_worked_hours_standard():
    schedule = WorkSchedule(
        name="Test",
        schedule_type="5/2",
        work_start=datetime.time(9, 0),
        work_end=datetime.time(18, 0),
        break_start=datetime.time(13, 0),
        break_end=datetime.time(14, 0),
        working_days=[1, 2, 3, 4, 5],
    )
    worked, overtime = calculate_worked_hours(datetime.time(9, 0), datetime.time(18, 0), schedule)
    assert worked == Decimal("8.00")
    assert overtime == Decimal("0.00")


def test_calculate_worked_hours_overtime():
    schedule = WorkSchedule(
        name="Test",
        schedule_type="5/2",
        work_start=datetime.time(9, 0),
        work_end=datetime.time(18, 0),
        break_start=datetime.time(13, 0),
        break_end=datetime.time(14, 0),
        working_days=[1, 2, 3, 4, 5],
    )
    worked, overtime = calculate_worked_hours(datetime.time(9, 0), datetime.time(20, 0), schedule)
    assert worked == Decimal("10.0")
    assert overtime == Decimal("2.0")
