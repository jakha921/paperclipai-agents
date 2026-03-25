from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from apps.core.models import SoftDeleteMixin, TimestampedModel
from apps.core.validators import validate_inn, validate_pinfl, validate_uzbekistan_phone


class Department(MPTTModel, TimestampedModel):
    """Подразделение университета."""

    class DepartmentType(models.TextChoices):
        RECTORATE = "RECTORATE", _("Ректорат")
        FACULTY = "FACULTY", _("Факультет")
        DEPARTMENT = "DEPARTMENT", _("Кафедра")
        ADMIN_SERVICE = "ADMIN_SERVICE", _("Административная служба")
        SUPPORT_UNIT = "SUPPORT_UNIT", _("Вспомогательное подразделение")

    name = models.JSONField(verbose_name=_("Название"), default=dict)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Код"))
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Родительское подразделение"),
    )
    department_type = models.CharField(
        max_length=20,
        choices=DepartmentType.choices,
        default=DepartmentType.DEPARTMENT,
        verbose_name=_("Тип подразделения"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Активно"))
    head = models.ForeignKey(
        "Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments",
        verbose_name=_("Руководитель"),
    )

    class MPTTMeta:
        order_insertion_by = ["code"]

    class Meta:
        verbose_name = _("Подразделение")
        verbose_name_plural = _("Подразделения")

    def __str__(self) -> str:
        return self.name.get("ru", self.code)

    def get_name(self, lang: str = "ru") -> str:
        return self.name.get(lang, self.name.get("ru", self.code))


class Position(TimestampedModel):
    """Должность."""

    class Category(models.TextChoices):
        PPS = "PPS", _("ППС (Профессорско-преподавательский состав)")
        NS = "NS", _("НС (Научный сотрудник)")
        AUP = "AUP", _("АУП (Административно-управленческий персонал)")
        UVP = "UVP", _("УВП (Учебно-вспомогательный персонал)")
        POP = "POP", _("ПОП (Прочий обслуживающий персонал)")

    name = models.JSONField(verbose_name=_("Название"), default=dict)
    code = models.CharField(max_length=20, unique=True, verbose_name=_("Код"))
    category = models.CharField(
        max_length=10,
        choices=Category.choices,
        verbose_name=_("Категория"),
    )
    min_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Минимальная зарплата"),
    )
    max_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Максимальная зарплата"),
    )
    is_academic = models.BooleanField(default=False, verbose_name=_("Академическая"))
    requirements = models.TextField(blank=True, verbose_name=_("Требования"))

    class Meta:
        verbose_name = _("Должность")
        verbose_name_plural = _("Должности")
        ordering = ["code"]

    def __str__(self) -> str:
        return self.name.get("ru", self.code)


class Employee(TimestampedModel, SoftDeleteMixin):
    """Сотрудник."""

    class ContractType(models.TextChoices):
        PERMANENT = "PERMANENT", _("Основное место работы")
        PART_TIME = "PART_TIME", _("Совместительство")
        HOURLY = "HOURLY", _("Почасовая оплата")

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Работает")
        ON_LEAVE = "ON_LEAVE", _("В отпуске")
        DISMISSED = "DISMISSED", _("Уволен")

    class Gender(models.TextChoices):
        MALE = "MALE", _("Мужской")
        FEMALE = "FEMALE", _("Женский")

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee",
        verbose_name=_("Пользователь"),
    )
    employee_number = models.CharField(
        max_length=20, unique=True, blank=True, verbose_name=_("Табельный номер")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
        verbose_name=_("Подразделение"),
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name="employees",
        verbose_name=_("Должность"),
    )
    hire_date = models.DateField(verbose_name=_("Дата принятия"))
    contract_type = models.CharField(
        max_length=15,
        choices=ContractType.choices,
        default=ContractType.PERMANENT,
        verbose_name=_("Тип договора"),
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("Статус"),
    )
    # Персональные данные
    first_name = models.CharField(max_length=100, verbose_name=_("Имя"))
    last_name = models.CharField(max_length=100, verbose_name=_("Фамилия"))
    middle_name = models.CharField(max_length=100, blank=True, verbose_name=_("Отчество"))
    pinfl = models.CharField(
        max_length=14,
        unique=True,
        validators=[validate_pinfl],
        verbose_name=_("ПИНФЛ"),
    )
    inn = models.CharField(
        max_length=9,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_inn],
        verbose_name=_("ИНН"),
    )
    passport_series = models.CharField(max_length=9, verbose_name=_("Серия и номер паспорта"))
    birth_date = models.DateField(verbose_name=_("Дата рождения"))
    gender = models.CharField(max_length=6, choices=Gender.choices, verbose_name=_("Пол"))
    nationality = models.CharField(max_length=50, verbose_name=_("Национальность"))
    # Контакты
    phone = models.CharField(
        max_length=20,
        validators=[validate_uzbekistan_phone],
        verbose_name=_("Телефон"),
    )
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    address = models.TextField(blank=True, verbose_name=_("Адрес"))
    # Фото
    photo = models.ImageField(upload_to="employees/", null=True, blank=True, verbose_name=_("Фото"))

    class Meta:
        verbose_name = _("Сотрудник")
        verbose_name_plural = _("Сотрудники")
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)


class EmploymentHistory(TimestampedModel):
    """История трудоустройства сотрудника."""

    class ChangeReason(models.TextChoices):
        HIRED = "HIRED", _("Принят на работу")
        TRANSFERRED = "TRANSFERRED", _("Переведён")
        PROMOTED = "PROMOTED", _("Повышен")
        DISMISSED = "DISMISSED", _("Уволен")

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name=_("Сотрудник"),
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        verbose_name=_("Подразделение"),
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        verbose_name=_("Должность"),
    )
    start_date = models.DateField(verbose_name=_("Дата начала"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("Дата окончания"))
    order_number = models.CharField(max_length=50, verbose_name=_("Номер приказа"))
    order_date = models.DateField(verbose_name=_("Дата приказа"))
    change_reason = models.CharField(
        max_length=20,
        choices=ChangeReason.choices,
        verbose_name=_("Причина изменения"),
    )

    class Meta:
        verbose_name = _("История занятости")
        verbose_name_plural = _("История занятости")
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.employee} — {self.position} ({self.start_date})"
