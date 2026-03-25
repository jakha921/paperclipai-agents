from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class AppraisalCycle(TimestampedModel):
    """Цикл аттестации."""

    class Status(models.TextChoices):
        PLANNING = "planning", _("Планирование")
        ACTIVE = "active", _("Активный")
        REVIEW = "review", _("Рассмотрение")
        COMPLETED = "completed", _("Завершён")

    name = models.CharField(max_length=200, verbose_name=_("Название"))
    start_date = models.DateField(verbose_name=_("Дата начала"))
    end_date = models.DateField(verbose_name=_("Дата окончания"))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING,
        verbose_name=_("Статус"),
    )
    applicable_departments = models.ManyToManyField(
        "departments.Department",
        blank=True,
        related_name="appraisal_cycles",
        verbose_name=_("Применимые подразделения"),
    )

    class Meta:
        verbose_name = _("Цикл аттестации")
        verbose_name_plural = _("Циклы аттестации")
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return self.name


class KPIIndicator(TimestampedModel):
    """Показатель KPI."""

    class Category(models.TextChoices):
        ACADEMIC = "academic", _("Академическая")
        ADMINISTRATIVE = "administrative", _("Административная")
        RESEARCH = "research", _("Научная")
        SERVICE = "service", _("Служебная")

    name = models.JSONField(default=dict, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        verbose_name=_("Категория"),
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Вес"),
    )
    max_score = models.IntegerField(default=10, verbose_name=_("Максимальный балл"))

    class Meta:
        verbose_name = _("Показатель KPI")
        verbose_name_plural = _("Показатели KPI")
        ordering = ["category", "name"]

    def __str__(self) -> str:
        return self.name.get("ru", str(self.pk))


class EmployeeAppraisal(TimestampedModel):
    """Аттестация сотрудника."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Ожидание")
        SELF_REVIEW = "self_review", _("Самооценка")
        MANAGER_REVIEW = "manager_review", _("Оценка руководителя")
        COMPLETED = "completed", _("Завершена")

    cycle = models.ForeignKey(
        AppraisalCycle,
        on_delete=models.CASCADE,
        related_name="appraisals",
        verbose_name=_("Цикл"),
    )
    employee = models.ForeignKey(
        "departments.Employee",
        on_delete=models.CASCADE,
        related_name="appraisals",
        verbose_name=_("Сотрудник"),
    )
    reviewer = models.ForeignKey(
        "departments.Employee",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviews",
        verbose_name=_("Ревьюер"),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Статус"),
    )
    overall_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Итоговый балл"),
    )
    comments = models.TextField(blank=True, verbose_name=_("Комментарии"))
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата проверки"))

    class Meta:
        verbose_name = _("Аттестация сотрудника")
        verbose_name_plural = _("Аттестации сотрудников")
        unique_together = [["cycle", "employee"]]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.employee} — {self.cycle}"


class AppraisalScore(TimestampedModel):
    """Оценка по KPI."""

    appraisal = models.ForeignKey(
        EmployeeAppraisal,
        on_delete=models.CASCADE,
        related_name="scores",
        verbose_name=_("Аттестация"),
    )
    kpi = models.ForeignKey(
        KPIIndicator,
        on_delete=models.PROTECT,
        verbose_name=_("Показатель KPI"),
    )
    self_score = models.IntegerField(null=True, blank=True, verbose_name=_("Самооценка"))
    manager_score = models.IntegerField(
        null=True, blank=True, verbose_name=_("Оценка руководителя")
    )
    final_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Итоговая оценка"),
    )
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))

    class Meta:
        verbose_name = _("Оценка KPI")
        verbose_name_plural = _("Оценки KPI")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.appraisal.employee} — {self.kpi}"


class TrainingProgram(TimestampedModel):
    """Программа обучения."""

    class TrainingType(models.TextChoices):
        INTERNAL = "internal", _("Внутренняя")
        EXTERNAL = "external", _("Внешняя")
        ONLINE = "online", _("Онлайн")

    name = models.JSONField(default=dict, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    provider = models.CharField(max_length=200, blank=True, verbose_name=_("Провайдер"))
    training_type = models.CharField(
        max_length=20,
        choices=TrainingType.choices,
        verbose_name=_("Тип обучения"),
    )
    duration_hours = models.IntegerField(default=0, verbose_name=_("Продолжительность (часы)"))
    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("Стоимость"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))

    class Meta:
        verbose_name = _("Программа обучения")
        verbose_name_plural = _("Программы обучения")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name.get("ru", str(self.pk))


class TrainingRecord(TimestampedModel):
    """Запись об обучении сотрудника."""

    class Status(models.TextChoices):
        ENROLLED = "enrolled", _("Зачислен")
        IN_PROGRESS = "in_progress", _("В процессе")
        COMPLETED = "completed", _("Завершён")
        CANCELLED = "cancelled", _("Отменён")

    employee = models.ForeignKey(
        "departments.Employee",
        on_delete=models.CASCADE,
        related_name="training_records",
        verbose_name=_("Сотрудник"),
    )
    program = models.ForeignKey(
        TrainingProgram,
        on_delete=models.PROTECT,
        verbose_name=_("Программа"),
    )
    start_date = models.DateField(null=True, blank=True, verbose_name=_("Дата начала"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Дата окончания"))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ENROLLED,
        verbose_name=_("Статус"),
    )
    certificate_number = models.CharField(
        max_length=50, blank=True, verbose_name=_("Номер сертификата")
    )
    score = models.IntegerField(null=True, blank=True, verbose_name=_("Балл"))

    class Meta:
        verbose_name = _("Запись об обучении")
        verbose_name_plural = _("Записи об обучении")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.employee} — {self.program}"
