import datetime

import pytest

from apps.leaves.models import PublicHoliday
from apps.leaves.services import calculate_working_days


@pytest.mark.django_db
def test_working_days_week():
    result = calculate_working_days(datetime.date(2025, 1, 6), datetime.date(2025, 1, 10))
    assert result == 5


@pytest.mark.django_db
def test_working_days_through_holiday():
    PublicHoliday.objects.create(
        date=datetime.date(2025, 3, 21), name={"ru": "Навруз"}, is_working_day=False
    )
    # Mon 2025-03-17 to Fri 2025-03-21 (Navruz on Fri) = 4 days
    result = calculate_working_days(datetime.date(2025, 3, 17), datetime.date(2025, 3, 21))
    assert result == 4


@pytest.mark.django_db
def test_working_days_weekend():
    result = calculate_working_days(datetime.date(2025, 1, 11), datetime.date(2025, 1, 12))
    assert result == 0


@pytest.mark.django_db
def test_working_days_start_after_end():
    result = calculate_working_days(datetime.date(2025, 1, 10), datetime.date(2025, 1, 6))
    assert result == 0
