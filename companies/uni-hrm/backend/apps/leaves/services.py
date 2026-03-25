from __future__ import annotations

from datetime import date, timedelta

from apps.leaves.models import PublicHoliday


def calculate_working_days(start: date, end: date) -> int:
    """Рабочие дни без суббот, воскресений и PublicHoliday."""
    if start > end:
        return 0
    holidays = set(
        PublicHoliday.objects.filter(date__range=[start, end], is_working_day=False).values_list(
            "date", flat=True
        )
    )
    count = 0
    current = start
    while current <= end:
        if current.weekday() < 5 and current not in holidays:
            count += 1
        current += timedelta(days=1)
    return count
