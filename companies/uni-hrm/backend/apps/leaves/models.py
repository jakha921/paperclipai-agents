from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class PublicHoliday(TimestampedModel):
    """Государственные праздники."""

    date = models.DateField(unique=True, verbose_name=_("Дата"))
    name = models.JSONField(default=dict, verbose_name=_("Название"))
    is_working_day = models.BooleanField(default=False, verbose_name=_("Рабочий день (перенос)"))

    class Meta:
        verbose_name = _("Государственный праздник")
        verbose_name_plural = _("Государственные праздники")
        ordering = ["date"]

    def __str__(self) -> str:
        return f"{self.date}: {self.name.get('ru', '')}"


class LeaveType(TimestampedModel):
    """Тип отпуска."""

    name = models.JSONField(default=dict, verbose_name=_("Название"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Код"))
    days_per_year = models.PositiveIntegerField(verbose_name=_("Дней в год"))
    is_paid = models.BooleanField(default=True, verbose_name=_("Оплачиваемый"))
    requires_document = models.BooleanField(default=False, verbose_name=_("Требует документ"))
    applicable_categories = models.JSONField(default=list, verbose_name=_("Применимые категории"))

    class Meta:
        verbose_name = _("Тип отпуска")
        verbose_name_plural = _("Типы отпусков")
        ordering = ["code"]

    def __str__(self) -> str:
        return self.code


class LeaveAllocation(TimestampedModel):
    """Начисление отпускных дней сотруднику."""

    employee = models.ForeignKey(
        "departments.Employee",
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name=_("Сотрудник"),
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.CASCADE, verbose_name=_("Тип отпуска")
    )
    year = models.PositiveIntegerField(verbose_name=_("Год"))
    total_days = models.PositiveIntegerField(verbose_name=_("Всего дней"))
    used_days = models.PositiveIntegerField(default=0, verbose_name=_("Использовано дней"))
    carry_over_days = models.PositiveIntegerField(default=0, verbose_name=_("Перенесённые дни"))

    class Meta:
        verbose_name = _("Начисление отпуска")
        verbose_name_plural = _("Начисления отпусков")
        unique_together = [["employee", "leave_type", "year"]]
        ordering = ["-year"]

    @property
    def remaining_days(self) -> int:
        return self.total_days + self.carry_over_days - self.used_days

    def __str__(self) -> str:
        return f"{self.employee} — {self.leave_type} ({self.year})"


class LeaveRequest(TimestampedModel):
    """Заявка на отпуск."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Черновик")
        PENDING_HEAD = "PENDING_HEAD", _("На рассмотрении у руководителя")
        PENDING_HR = "PENDING_HR", _("На рассмотрении HR")
        APPROVED = "APPROVED", _("Одобрено")
        REJECTED = "REJECTED", _("Отклонено")
        CANCELLED = "CANCELLED", _("Отменено")

    employee = models.ForeignKey(
        "departments.Employee",
        on_delete=models.CASCADE,
        related_name="leave_requests",
        verbose_name=_("Сотрудник"),
    )
    leave_type = models.ForeignKey(
        LeaveType, on_delete=models.PROTECT, verbose_name=_("Тип отпуска")
    )
    start_date = models.DateField(verbose_name=_("Дата начала"))
    end_date = models.DateField(verbose_name=_("Дата окончания"))
    days_count = models.PositiveIntegerField(default=0, verbose_name=_("Количество дней"))
    reason = models.TextField(blank=True, verbose_name=_("Причина"))
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Статус"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_leave_requests",
        verbose_name=_("Одобрил"),
    )
    rejection_reason = models.TextField(blank=True, verbose_name=_("Причина отклонения"))

    class Meta:
        verbose_name = _("Заявка на отпуск")
        verbose_name_plural = _("Заявки на отпуск")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.employee} — {self.leave_type} ({self.start_date} — {self.end_date})"
