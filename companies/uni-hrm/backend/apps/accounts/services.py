import random
import string
from datetime import timedelta

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from apps.accounts.models import OTPCode, User


class OTPService:
    """Сервис для генерации и верификации OTP кодов."""

    CODE_LENGTH = 6
    EXPIRY_MINUTES = 5
    MAX_ATTEMPTS = 3

    @classmethod
    def generate(cls, user: User) -> OTPCode:
        """Генерирует OTP код для пользователя. Возвращает OTPCode объект."""
        # Деактивируем предыдущие неиспользованные коды
        OTPCode.objects.filter(user=user, is_used=False).update(is_used=True)

        code = "".join(random.choices(string.digits, k=cls.CODE_LENGTH))
        return OTPCode.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=cls.EXPIRY_MINUTES),
        )

    @classmethod
    def verify(cls, user: User, code: str) -> bool:
        """Верифицирует OTP код. Возвращает True при успехе, иначе поднимает ValidationError."""
        otp = (
            OTPCode.objects.filter(
                user=user,
                is_used=False,
                expires_at__gt=timezone.now(),
            )
            .order_by("-created_at")
            .first()
        )

        if otp is None:
            raise ValidationError(_("Код не найден или истёк."))

        if otp.attempts >= cls.MAX_ATTEMPTS:
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            raise ValidationError(_("Превышено максимальное количество попыток."))

        if otp.code != code:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            raise ValidationError(_("Неверный код."))

        otp.is_used = True
        otp.save(update_fields=["is_used", "attempts"])

        # Верифицируем пользователя
        user.is_verified = True
        user.save(update_fields=["is_verified"])

        return True
