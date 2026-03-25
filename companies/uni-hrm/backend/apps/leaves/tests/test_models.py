import datetime

import pytest

from apps.leaves.models import LeaveAllocation, LeaveType, PublicHoliday
from apps.leaves.services import calculate_working_days


@pytest.mark.django_db
def test_leave_allocation_remaining_days():
    leave_type = LeaveType.objects.create(
        name={"ru": "Test"}, code="TEST_REMAINING", days_per_year=24
    )
    alloc = LeaveAllocation(
        leave_type=leave_type, year=2025, total_days=24, used_days=5, carry_over_days=2
    )
    assert alloc.remaining_days == 21  # 24 + 2 - 5


@pytest.mark.django_db
def test_calculate_working_days_simple():
    # Mon 2025-01-06 to Fri 2025-01-10 = 5 days
    result = calculate_working_days(datetime.date(2025, 1, 6), datetime.date(2025, 1, 10))
    assert result == 5


@pytest.mark.django_db
def test_calculate_working_days_excludes_weekend():
    # Mon 2025-01-06 to Sun 2025-01-12 = 5 working days (Sat+Sun excluded)
    result = calculate_working_days(datetime.date(2025, 1, 6), datetime.date(2025, 1, 12))
    assert result == 5


@pytest.mark.django_db
def test_calculate_working_days_excludes_holiday():
    # Create a holiday on Wednesday
    PublicHoliday.objects.create(
        date=datetime.date(2025, 1, 8),
        name={"ru": "Test Holiday"},
        is_working_day=False,
    )
    # Mon 2025-01-06 to Fri 2025-01-10 with holiday on Wed = 4 days
    result = calculate_working_days(datetime.date(2025, 1, 6), datetime.date(2025, 1, 10))
    assert result == 4
