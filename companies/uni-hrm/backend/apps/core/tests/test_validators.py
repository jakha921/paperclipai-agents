import pytest
from django.core.exceptions import ValidationError

from apps.core.validators import validate_inn, validate_pinfl, validate_uzbekistan_phone


class TestValidatePinfl:
    def _make_pinfl(
        self,
        year: str = "1990",
        month: str = "01",
        day: str = "15",
        gender_century: str = "3",
        region: str = "700",
    ) -> str:
        """Создаёт ПИНФЛ с корректной контрольной суммой."""
        base = f"{year}{month}{day}{gender_century}{region}"
        weights = [7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
        digits = [int(d) for d in base]
        checksum = sum(d * w for d, w in zip(digits, weights)) % 100
        return f"{base}{checksum:02d}"

    def test_valid_pinfl(self):
        pinfl = self._make_pinfl()
        validate_pinfl(pinfl)  # Не должно быть ошибки

    def test_valid_pinfl_female_20th_century(self):
        pinfl = self._make_pinfl(gender_century="4")
        validate_pinfl(pinfl)

    def test_valid_pinfl_21st_century(self):
        pinfl = self._make_pinfl(year="2005", month="06", day="20", gender_century="5")
        validate_pinfl(pinfl)

    def test_invalid_format_too_short(self):
        with pytest.raises(ValidationError, match="14 цифр"):
            validate_pinfl("1234567890123")

    def test_invalid_format_too_long(self):
        with pytest.raises(ValidationError, match="14 цифр"):
            validate_pinfl("123456789012345")

    def test_invalid_format_non_digits(self):
        with pytest.raises(ValidationError, match="14 цифр"):
            validate_pinfl("1990011537001a")

    def test_invalid_gender_century_zero(self):
        # gender_century=0 — невалидно
        base = "19900115" + "0" + "700"
        weights = [7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
        digits = [int(d) for d in base]
        checksum = sum(d * w for d, w in zip(digits, weights)) % 100
        pinfl = f"{base}{checksum:02d}"
        with pytest.raises(ValidationError, match="код пола и века"):
            validate_pinfl(pinfl)

    def test_invalid_gender_century_seven(self):
        base = "19900115" + "7" + "700"
        weights = [7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
        digits = [int(d) for d in base]
        checksum = sum(d * w for d, w in zip(digits, weights)) % 100
        pinfl = f"{base}{checksum:02d}"
        with pytest.raises(ValidationError, match="код пола и века"):
            validate_pinfl(pinfl)

    def test_invalid_year_century_mismatch(self):
        # Год 1990, но gender_century=5 (21 век)
        base = "19900115" + "5" + "700"
        weights = [7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
        digits = [int(d) for d in base]
        checksum = sum(d * w for d, w in zip(digits, weights)) % 100
        pinfl = f"{base}{checksum:02d}"
        with pytest.raises(ValidationError, match="Год рождения не соответствует"):
            validate_pinfl(pinfl)

    def test_invalid_date_month_13(self):
        base = "19901315" + "3" + "700"
        weights = [7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
        digits = [int(d) for d in base]
        checksum = sum(d * w for d, w in zip(digits, weights)) % 100
        pinfl = f"{base}{checksum:02d}"
        with pytest.raises(ValidationError, match="Некорректная дата рождения"):
            validate_pinfl(pinfl)

    def test_invalid_date_day_32(self):
        base = "19900132" + "3" + "700"
        weights = [7, 3, 1, 7, 3, 1, 7, 3, 1, 7, 3, 1]
        digits = [int(d) for d in base]
        checksum = sum(d * w for d, w in zip(digits, weights)) % 100
        pinfl = f"{base}{checksum:02d}"
        with pytest.raises(ValidationError, match="Некорректная дата рождения"):
            validate_pinfl(pinfl)

    def test_invalid_checksum(self):
        pinfl = self._make_pinfl()
        # Подменяем контрольную сумму
        wrong_checksum = (int(pinfl[12:14]) + 1) % 100
        bad_pinfl = pinfl[:12] + f"{wrong_checksum:02d}"
        with pytest.raises(ValidationError, match="контрольная сумма"):
            validate_pinfl(bad_pinfl)


class TestValidateInn:
    def test_valid_inn(self):
        validate_inn("123456789")  # Не должно быть ошибки

    def test_valid_inn_different_digits(self):
        validate_inn("987654321")

    def test_invalid_format_too_short(self):
        with pytest.raises(ValidationError, match="9 цифр"):
            validate_inn("12345678")

    def test_invalid_format_too_long(self):
        with pytest.raises(ValidationError, match="9 цифр"):
            validate_inn("1234567890")

    def test_invalid_format_non_digits(self):
        with pytest.raises(ValidationError, match="9 цифр"):
            validate_inn("12345678a")

    def test_invalid_all_same_digits(self):
        with pytest.raises(ValidationError, match="одинаковых цифр"):
            validate_inn("111111111")

    def test_invalid_all_zeros(self):
        with pytest.raises(ValidationError, match="одинаковых цифр"):
            validate_inn("000000000")


class TestValidateUzbekistanPhone:
    def test_valid_phone(self):
        validate_uzbekistan_phone("+998901234567")

    def test_valid_phone_different_code(self):
        validate_uzbekistan_phone("+998712345678")

    def test_invalid_no_plus(self):
        with pytest.raises(ValidationError, match="\\+998XXXXXXXXX"):
            validate_uzbekistan_phone("998901234567")

    def test_invalid_wrong_country_code(self):
        with pytest.raises(ValidationError, match="\\+998XXXXXXXXX"):
            validate_uzbekistan_phone("+997901234567")

    def test_invalid_too_short(self):
        with pytest.raises(ValidationError, match="\\+998XXXXXXXXX"):
            validate_uzbekistan_phone("+99890123456")

    def test_invalid_too_long(self):
        with pytest.raises(ValidationError, match="\\+998XXXXXXXXX"):
            validate_uzbekistan_phone("+9989012345678")

    def test_invalid_letters(self):
        with pytest.raises(ValidationError, match="\\+998XXXXXXXXX"):
            validate_uzbekistan_phone("+998abcdefghi")
