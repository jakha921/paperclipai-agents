from __future__ import annotations

import datetime

from django.core.management.base import BaseCommand

from apps.leaves.models import LeaveType, PublicHoliday

LEAVE_TYPES = [
    {
        "code": "ANNUAL_PPS",
        "name": {"ru": "Ежегодный (ППС)", "uz": "Yillik (PPS)", "en": "Annual (PPS)"},
        "days_per_year": 56,
        "is_paid": True,
        "requires_document": False,
        "applicable_categories": ["PPS"],
    },
    {
        "code": "ANNUAL_AUP",
        "name": {"ru": "Ежегодный (АУП)", "uz": "Yillik (AUP)", "en": "Annual (AUP)"},
        "days_per_year": 24,
        "is_paid": True,
        "requires_document": False,
        "applicable_categories": ["AUP", "UVP", "POP"],
    },
    {
        "code": "ANNUAL_NS",
        "name": {"ru": "Ежегодный (НС)", "uz": "Yillik (NS)", "en": "Annual (NS)"},
        "days_per_year": 36,
        "is_paid": True,
        "requires_document": False,
        "applicable_categories": ["NS"],
    },
    {
        "code": "SICK",
        "name": {"ru": "Больничный", "uz": "Kasallik", "en": "Sick Leave"},
        "days_per_year": 120,
        "is_paid": True,
        "requires_document": True,
        "applicable_categories": [],
    },
    {
        "code": "MATERNITY",
        "name": {"ru": "Декретный", "uz": "Tug'ruq ta'tili", "en": "Maternity Leave"},
        "days_per_year": 126,
        "is_paid": True,
        "requires_document": True,
        "applicable_categories": ["PPS", "AUP", "UVP", "POP", "NS"],
    },
    {
        "code": "UNPAID",
        "name": {"ru": "За свой счёт", "uz": "O'z hisobiga", "en": "Unpaid Leave"},
        "days_per_year": 30,
        "is_paid": False,
        "requires_document": False,
        "applicable_categories": [],
    },
    {
        "code": "EDUCATIONAL",
        "name": {"ru": "Учебный", "uz": "Ta'lim ta'tili", "en": "Educational Leave"},
        "days_per_year": 40,
        "is_paid": True,
        "requires_document": True,
        "applicable_categories": [],
    },
]

HOLIDAYS = [
    (1, 1, {"ru": "Новый год", "uz": "Yangi yil", "en": "New Year"}),
    (3, 8, {"ru": "День женщин", "uz": "Xalqaro xotin-qizlar kuni", "en": "Women's Day"}),
    (3, 21, {"ru": "Навруз", "uz": "Navro'z", "en": "Navruz"}),
    (5, 9, {"ru": "День памяти", "uz": "Xotira kuni", "en": "Remembrance Day"}),
    (9, 1, {"ru": "День независимости", "uz": "Mustaqillik kuni", "en": "Independence Day"}),
    (10, 1, {"ru": "День учителя", "uz": "O'qituvchilar kuni", "en": "Teachers' Day"}),
    (12, 8, {"ru": "День Конституции", "uz": "Konstitutsiya kuni", "en": "Constitution Day"}),
]


class Command(BaseCommand):
    help = "Seed leave types and public holidays for Uzbekistan"

    def handle(self, *args, **kwargs) -> None:
        for lt_data in LEAVE_TYPES:
            LeaveType.objects.update_or_create(code=lt_data["code"], defaults=lt_data)
            self.stdout.write(f"  LeaveType: {lt_data['code']}")

        for year in [2024, 2025, 2026]:
            for month, day, name in HOLIDAYS:
                PublicHoliday.objects.update_or_create(
                    date=datetime.date(year, month, day),
                    defaults={"name": name, "is_working_day": False},
                )

        self.stdout.write(self.style.SUCCESS("Leaves seeded successfully."))
