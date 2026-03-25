import re
from datetime import date

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_pinfl(value: str) -> None:
    """
    Валидатор ПИНФЛ (Персональный идентификационный номер физического лица).

    Проверяет:
    - Длину (14 цифр)
    - Формат (только цифры)
    - Корректность даты рождения
    - Корректность кода пола/века
    - Контрольную сумму
    """
    if not re.match(r"^\d{14}$", value):
        raise ValidationError(
            _("ПИНФЛ должен содержать ровно 14 цифр."),
            code="invalid_pinfl_format",
        )

    year = int(value[0:4])
    month = int(value[4:6])
    day = int(value[6:8])
    gender_century = int(value[8])
    region = int(value[9:12])
    checksum = int(value[12:14])

    # Проверка кода пола и века
    if gender_century not in range(1, 7):
        raise ValidationError(
            _("Некорректный код пола и века в ПИНФЛ."),
            code="invalid_pinfl_gender",
        )

    # Проверка соответствия века и года
    century_map = {
        1: (1800, 1899),
        2: (1800, 1899),
        3: (1900, 1999),
        4: (1900, 1999),
        5: (2000, 2099),
        6: (2000, 2099),
    }
    min_year, max_year = century_map[gender_century]
    if not (min_year <= year <= max_year):
        raise ValidationError(
            _("Год рождения не соответствует коду века в ПИНФЛ."),
            code="invalid_pinfl_year",
        )

    # Проверка даты рождения
    try:
        birth_date = date(year, month, day)
        if birth_date > date.today():
            raise ValidationError(
                _("Дата рождения в ПИНФЛ не может быть в будущем."),
                code="invalid_pinfl_future_date",
            )
    except ValueError:
        raise ValidationError(
            _("Некорректная дата рождения в ПИНФЛ."),
            code="invalid_pinfl_date",
        )

    # Проверка кода региона
    if not (1 <= region <= 799):
        raise ValidationError(
            _("Некорректный код региона в ПИНФЛ."),
            code="invalid_pinfl_region",
        )

    # Проверка контрольной суммы
    weights = [7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
    digits = [int(d) for d in value[:12]]
    calculated_checksum = sum(d * w for d, w in zip(digits, weights)) % 100

    if calculated_checksum != checksum:
        raise ValidationError(
            _("Некорректная контрольная сумма ПИНФЛ."),
            code="invalid_pinfl_checksum",
        )


def validate_inn(value: str) -> None:
    """
    Валидатор ИНН (Идентификационный номер налогоплательщика) для физических лиц.

    Проверяет:
    - Длину (9 цифр)
    - Формат (только цифры)
    - Не состоит из одинаковых цифр
    """
    if not re.match(r"^\d{9}$", value):
        raise ValidationError(
            _("ИНН должен содержать ровно 9 цифр."),
            code="invalid_inn_format",
        )

    # Проверка, что не состоит из одинаковых цифр
    if len(set(value)) == 1:
        raise ValidationError(
            _("ИНН не может состоять из одинаковых цифр."),
            code="invalid_inn_pattern",
        )


def validate_uzbekistan_phone(value: str) -> None:
    """Валидатор номера телефона Узбекистана."""
    pattern = r"^\+998\d{9}$"
    if not re.match(pattern, value):
        raise ValidationError(
            _("Номер телефона должен быть в формате +998XXXXXXXXX"),
            code="invalid_phone",
        )
