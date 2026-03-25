from __future__ import annotations

import datetime

from django.core.management.base import BaseCommand

from apps.attendance.models import WorkSchedule


class Command(BaseCommand):
    help = "Seed work schedules"

    def handle(self, *args, **kwargs) -> None:
        WorkSchedule.objects.update_or_create(
            name="Стандартный 5/2",
            defaults={
                "schedule_type": WorkSchedule.ScheduleType.FIVE_TWO,
                "work_start": datetime.time(9, 0),
                "work_end": datetime.time(18, 0),
                "break_start": datetime.time(13, 0),
                "break_end": datetime.time(14, 0),
                "working_days": [1, 2, 3, 4, 5],
            },
        )
        WorkSchedule.objects.update_or_create(
            name="Стандартный 6/1",
            defaults={
                "schedule_type": WorkSchedule.ScheduleType.SIX_ONE,
                "work_start": datetime.time(9, 0),
                "work_end": datetime.time(17, 0),
                "break_start": None,
                "break_end": None,
                "working_days": [1, 2, 3, 4, 5, 6],
            },
        )
        self.stdout.write(self.style.SUCCESS("Attendance schedules seeded."))
