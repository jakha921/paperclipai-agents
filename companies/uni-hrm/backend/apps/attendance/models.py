from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class WorkSchedule(TimestampedModel):
    class ScheduleType(models.TextChoices):
        FIVE_TWO = "5/2", _("5/2 (пн-пт)")
        SIX_ONE = "6/1", _("6/1 (пн-сб)")
        SHIFT = "SHIFT", _("Сменный")
        FLEXIBLE = "FLEXIBLE", _("Гибкий")

    name = models.CharField(max_length=100, verbose_name=_("Название"))
    schedule_type = models.CharField(
        max_length=10, choices=ScheduleType.choices, verbose_name=_("Тип")
    )
    work_start = models.TimeField(verbose_name=_("Начало работы"))
    work_end = models.TimeField(verbose_name=_("Конец работы"))
    break_start = models.TimeField(null=True, blank=True, verbose_name=_("Начало перерыва"))
    break_end = models.TimeField(null=True, blank=True, verbose_name=_("Конец перерыва"))
    working_days = models.JSONField(default=list, verbose_name=_("Рабочие дни"))

    class Meta:
        verbose_name = _("Рабочий график")
        verbose_name_plural = _("Рабочие графики")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class EmployeeSchedule(TimestampedModel):
    employee = models.ForeignKey(
        "departments.Employee",
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name=_("Сотрудник"),
    )
    schedule = models.ForeignKey(WorkSchedule, on_delete=models.PROTECT, verbose_name=_("График"))
    effective_from = models.DateField(verbose_name=_("Действует с"))
    effective_to = models.DateField(null=True, blank=True, verbose_name=_("Действует по"))

    class Meta:
        verbose_name = _("График сотрудника")
        verbose_name_plural = _("Графики сотрудников")
        ordering = ["-effective_from"]

    def __str__(self) -> str:
        return f"{self.employee} — {self.schedule}"


class AttendanceRecord(TimestampedModel):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", _("Присутствовал")
        ABSENT = "ABSENT", _("Отсутствовал")
        LATE = "LATE", _("Опоздал")
        HALF_DAY = "HALF_DAY", _("Неполный день")
        ON_LEAVE = "ON_LEAVE", _("В отпуске")
        HOLIDAY = "HOLIDAY", _("Выходной/праздник")

    class Source(models.TextChoices):
        MANUAL = "MANUAL", _("Вручную")
        IMPORT = "IMPORT", _("Импорт")
        BIOMETRIC = "BIOMETRIC", _("Биометрия")

    employee = models.ForeignKey(
        "departments.Employee",
        on_delete=models.CASCADE,
        related_name="attendance",
        verbose_name=_("Сотрудник"),
    )
    date = models.DateField(verbose_name=_("Дата"))
    check_in = models.TimeField(null=True, blank=True, verbose_name=_("Приход"))
    check_out = models.TimeField(null=True, blank=True, verbose_name=_("Уход"))
    status = models.CharField(max_length=10, choices=Status.choices, verbose_name=_("Статус"))
    worked_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Рабочие часы")
    )
    overtime_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Сверхурочные")
    )
    source = models.CharField(
        max_length=10,
        choices=Source.choices,
        default=Source.MANUAL,
        verbose_name=_("Источник"),
    )
    note = models.TextField(blank=True, verbose_name=_("Примечание"))

    class Meta:
        verbose_name = _("Запись посещаемости")
        verbose_name_plural = _("Записи посещаемости")
        unique_together = [["employee", "date"]]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"{self.employee} — {self.date} ({self.status})"


class TimeSheet(TimestampedModel):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Черновик")
        SUBMITTED = "SUBMITTED", _("Отправлен")
        APPROVED = "APPROVED", _("Утверждён")

    employee = models.ForeignKey(
        "departments.Employee",
        on_delete=models.CASCADE,
        related_name="timesheets",
        verbose_name=_("Сотрудник"),
    )
    month = models.PositiveSmallIntegerField(verbose_name=_("Месяц"))
    year = models.PositiveSmallIntegerField(verbose_name=_("Год"))
    total_working_days = models.PositiveIntegerField(default=0, verbose_name=_("Рабочих дней"))
    days_present = models.PositiveIntegerField(default=0, verbose_name=_("Присутствовал"))
    days_absent = models.PositiveIntegerField(default=0, verbose_name=_("Отсутствовал"))
    days_late = models.PositiveIntegerField(default=0, verbose_name=_("Опоздал"))
    days_on_leave = models.PositiveIntegerField(default=0, verbose_name=_("В отпуске"))
    total_hours = models.DecimalField(
        max_digits=7, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Всего часов")
    )
    overtime_hours = models.DecimalField(
        max_digits=7, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Сверхурочные")
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Статус"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_timesheets",
        verbose_name=_("Утвердил"),
    )

    class Meta:
        verbose_name = _("Табель")
        verbose_name_plural = _("Табели")
        unique_together = [["employee", "month", "year"]]
        ordering = ["-year", "-month"]

    def __str__(self) -> str:
        return f"{self.employee} — {self.month}/{self.year}"
