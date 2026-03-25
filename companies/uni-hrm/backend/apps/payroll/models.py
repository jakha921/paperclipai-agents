from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class TaxConfiguration(TimestampedModel):
    """Налоговые ставки по году (Узбекистан)."""

    year = models.PositiveIntegerField(unique=True, verbose_name=_("Год"))
    ndfl_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal("0.12"), verbose_name=_("Ставка НДФЛ")
    )
    social_tax_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal("0.12"), verbose_name=_("Социальный налог")
    )
    inps_employee_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal("0.001"),
        verbose_name=_("ИНПС (сотрудник)"),
    )
    inps_employer_rate = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal("0.001"),
        verbose_name=_("ИНПС (работодатель)"),
    )
    minimum_wage = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1155000"),
        verbose_name=_("Минимальная зарплата"),
    )

    class Meta:
        ordering = ["-year"]
        verbose_name = _("Налоговая конфигурация")
        verbose_name_plural = _("Налоговые конфигурации")

    def __str__(self) -> str:
        return f"Tax Config {self.year}"


class EmployeeSalary(TimestampedModel):
    """История зарплат сотрудника."""

    employee = models.ForeignKey(
        "departments.Employee",
        on_delete=models.CASCADE,
        related_name="salaries",
        verbose_name=_("Сотрудник"),
    )
    effective_from = models.DateField(verbose_name=_("Действует с"))
    effective_to = models.DateField(null=True, blank=True, verbose_name=_("Действует по"))
    base_salary = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Базовый оклад")
    )
    academic_bonus_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Академическая надбавка %"),
    )
    position_bonus_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Должностная надбавка %"),
    )
    seniority_bonus_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0"), verbose_name=_("Надбавка за стаж %")
    )
    other_allowances = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("Прочие надбавки")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))

    class Meta:
        unique_together = [["employee", "effective_from"]]
        ordering = ["-effective_from"]
        verbose_name = _("Зарплата сотрудника")
        verbose_name_plural = _("Зарплаты сотрудников")

    def __str__(self) -> str:
        return f"{self.employee} — {self.base_salary} от {self.effective_from}"

    @property
    def gross_monthly(self) -> Decimal:
        """Расчётный оклад до корректировки посещаемости."""
        bonus_pct = self.academic_bonus_pct + self.position_bonus_pct + self.seniority_bonus_pct
        bonuses = self.base_salary * bonus_pct / Decimal("100")
        return self.base_salary + bonuses + self.other_allowances


class Payroll(TimestampedModel):
    """Расчётный лист сотрудника за месяц."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Черновик")
        CALCULATED = "CALCULATED", _("Рассчитано")
        APPROVED = "APPROVED", _("Одобрено")
        PAID = "PAID", _("Выплачено")

    employee = models.ForeignKey(
        "departments.Employee",
        on_delete=models.PROTECT,
        related_name="payrolls",
        verbose_name=_("Сотрудник"),
    )
    month = models.PositiveSmallIntegerField(verbose_name=_("Месяц"))
    year = models.PositiveSmallIntegerField(verbose_name=_("Год"))
    tax_config = models.ForeignKey(
        TaxConfiguration, on_delete=models.PROTECT, verbose_name=_("Налоговая конфигурация")
    )

    # Начисления
    base_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("Базовый оклад")
    )
    academic_bonus = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Академическая надбавка"),
    )
    position_bonus = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Должностная надбавка"),
    )
    seniority_bonus = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("Надбавка за стаж")
    )
    other_allowances = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("Прочие надбавки")
    )

    # Посещаемость
    working_days_in_month = models.PositiveIntegerField(
        default=0, verbose_name=_("Рабочих дней в месяце")
    )
    days_worked = models.PositiveIntegerField(default=0, verbose_name=_("Отработано дней"))
    days_on_leave = models.PositiveIntegerField(default=0, verbose_name=_("Дней в отпуске"))
    days_absent = models.PositiveIntegerField(default=0, verbose_name=_("Дней отсутствия"))
    overtime_hours = models.DecimalField(
        max_digits=7, decimal_places=2, default=Decimal("0"), verbose_name=_("Сверхурочные часы")
    )

    # Расчёт
    attendance_ratio = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        default=Decimal("1"),
        verbose_name=_("Коэффициент посещаемости"),
    )
    overtime_payment = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("Оплата сверхурочных")
    )
    gross_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("Начислено (gross)")
    )

    # Удержания
    ndfl = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("НДФЛ")
    )
    inps_employee = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("ИНПС (сотрудник)")
    )
    other_deductions = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("Прочие удержания")
    )
    total_deductions = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("Итого удержания")
    )

    # К выплате
    net_salary = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("К выплате (net)")
    )

    # Работодатель
    employer_social_tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name=_("Соц. налог работодателя"),
    )
    employer_inps = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"), verbose_name=_("ИНПС работодателя")
    )

    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.DRAFT, verbose_name=_("Статус")
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_payrolls",
        verbose_name=_("Одобрил"),
    )
    paid_date = models.DateField(null=True, blank=True, verbose_name=_("Дата выплаты"))

    class Meta:
        unique_together = [["employee", "month", "year"]]
        ordering = ["-year", "-month"]
        verbose_name = _("Расчётный лист")
        verbose_name_plural = _("Расчётные листы")

    def __str__(self) -> str:
        return f"{self.employee} — {self.month}/{self.year}"
