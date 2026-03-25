from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class AcademicDegree(TimestampedModel):
    """Академическая степень (PhD, DSc, Кандидат наук и т.д.)."""

    name = models.JSONField(default=dict, verbose_name=_("Название"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Код"))
    country = models.CharField(max_length=100, blank=True, verbose_name=_("Страна"))

    class Meta:
        verbose_name = _("Академическая степень")
        verbose_name_plural = _("Академические степени")
        ordering = ["code"]

    def __str__(self) -> str:
        return self.name.get("ru", self.code)


class AcademicTitle(TimestampedModel):
    """Академическое звание (Доцент, Профессор и т.д.)."""

    name = models.JSONField(default=dict, verbose_name=_("Название"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Код"))

    class Meta:
        verbose_name = _("Академическое звание")
        verbose_name_plural = _("Академические звания")
        ordering = ["code"]

    def __str__(self) -> str:
        return self.name.get("ru", self.code)


class EmployeeAcademic(TimestampedModel):
    """Академические данные сотрудника."""

    employee = models.OneToOneField(
        "departments.Employee",
        on_delete=models.CASCADE,
        related_name="academic",
        verbose_name=_("Сотрудник"),
    )
    degree = models.ForeignKey(
        AcademicDegree,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name=_("Степень"),
    )
    title = models.ForeignKey(
        AcademicTitle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
        verbose_name=_("Звание"),
    )
    specialization = models.CharField(max_length=255, blank=True, verbose_name=_("Специализация"))
    dissertation_topic = models.TextField(blank=True, verbose_name=_("Тема диссертации"))
    diploma_number = models.CharField(max_length=50, blank=True, verbose_name=_("Номер диплома"))
    awarded_date = models.DateField(null=True, blank=True, verbose_name=_("Дата присвоения"))

    class Meta:
        verbose_name = _("Академические данные сотрудника")
        verbose_name_plural = _("Академические данные сотрудников")

    def __str__(self) -> str:
        parts = [str(self.employee)]
        if self.degree:
            parts.append(str(self.degree))
        if self.title:
            parts.append(str(self.title))
        return " — ".join(parts)


class Subject(TimestampedModel):
    """Учебная дисциплина."""

    name = models.JSONField(default=dict, verbose_name=_("Название"))
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Код"))
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.PROTECT,
        related_name="subjects",
        verbose_name=_("Кафедра"),
    )
    credits = models.IntegerField(default=0, verbose_name=_("Кредиты"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активная"))

    class Meta:
        verbose_name = _("Дисциплина")
        verbose_name_plural = _("Дисциплины")
        ordering = ["code"]

    def __str__(self) -> str:
        return self.name.get("ru", self.code)


class AcademicLoad(TimestampedModel):
    """Учебная нагрузка преподавателя."""

    class LoadType(models.TextChoices):
        PRIMARY = "PRIMARY", _("Основная")
        SECONDARY = "SECONDARY", _("Совместительство")
        HOURLY = "HOURLY", _("Почасовая")

    employee = models.ForeignKey(
        "departments.Employee",
        on_delete=models.CASCADE,
        related_name="academic_loads",
        verbose_name=_("Преподаватель"),
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="loads",
        verbose_name=_("Дисциплина"),
    )
    academic_year = models.CharField(
        max_length=9, verbose_name=_("Учебный год")
    )  # e.g. "2024-2025"
    semester = models.IntegerField(
        choices=[(1, _("1-й семестр")), (2, _("2-й семестр"))],
        verbose_name=_("Семестр"),
    )
    lecture_hours = models.IntegerField(default=0, verbose_name=_("Лекции (часы)"))
    seminar_hours = models.IntegerField(default=0, verbose_name=_("Семинары (часы)"))
    lab_hours = models.IntegerField(default=0, verbose_name=_("Лабораторные (часы)"))
    load_type = models.CharField(
        max_length=10,
        choices=LoadType.choices,
        default=LoadType.PRIMARY,
        verbose_name=_("Тип нагрузки"),
    )

    class Meta:
        verbose_name = _("Учебная нагрузка")
        verbose_name_plural = _("Учебные нагрузки")
        unique_together = [["employee", "subject", "academic_year", "semester"]]
        ordering = ["-academic_year", "semester"]

    @property
    def total_hours(self) -> int:
        return self.lecture_hours + self.seminar_hours + self.lab_hours

    def __str__(self) -> str:
        return (
            f"{self.employee} — {self.subject} "
            f"({self.academic_year}, {self.get_semester_display()})"
        )


class PositionContest(TimestampedModel):
    """Конкурс на замещение должности."""

    class Status(models.TextChoices):
        OPEN = "OPEN", _("Открыт")
        CLOSED = "CLOSED", _("Закрыт")
        CANCELLED = "CANCELLED", _("Отменён")

    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.PROTECT,
        related_name="contests",
        verbose_name=_("Подразделение"),
    )
    position = models.ForeignKey(
        "departments.Position",
        on_delete=models.PROTECT,
        related_name="contests",
        verbose_name=_("Должность"),
    )
    requirements = models.TextField(blank=True, verbose_name=_("Требования"))
    application_deadline = models.DateField(verbose_name=_("Срок подачи заявок"))
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name=_("Статус"),
    )
    winner = models.ForeignKey(
        "departments.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_contests",
        verbose_name=_("Победитель"),
    )

    class Meta:
        verbose_name = _("Конкурс на должность")
        verbose_name_plural = _("Конкурсы на должности")
        ordering = ["-application_deadline"]

    def __str__(self) -> str:
        return f"{self.position} — {self.department} ({self.application_deadline})"
