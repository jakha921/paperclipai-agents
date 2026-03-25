from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel
from apps.core.validators import validate_uzbekistan_phone


class User(AbstractUser):
    """Пользователь системы Uni-HRM."""

    email = models.EmailField(_("email"), unique=True)
    phone = models.CharField(
        _("телефон"),
        max_length=13,
        blank=True,
        validators=[validate_uzbekistan_phone],
    )
    avatar = models.ImageField(
        _("аватар"),
        upload_to="avatars/%Y/%m/",
        blank=True,
    )
    language = models.CharField(
        _("язык"),
        max_length=2,
        choices=[("ru", _("Русский")), ("uz", _("O'zbek")), ("en", _("English"))],
        default="ru",
    )
    is_verified = models.BooleanField(_("верифицирован"), default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")
        ordering = ["-date_joined"]

    @property
    def full_name(self) -> str:
        return self.get_full_name() or self.email

    def __str__(self) -> str:
        return self.get_full_name() or self.email


class Permission(TimestampedModel):
    """Разрешение для RBAC."""

    codename = models.CharField(_("код"), max_length=100, unique=True)
    name = models.CharField(_("название"), max_length=255)
    module = models.CharField(_("модуль"), max_length=50)

    class Meta:
        verbose_name = _("разрешение")
        verbose_name_plural = _("разрешения")
        ordering = ["module", "codename"]

    def __str__(self) -> str:
        return f"{self.module}.{self.codename}"


class Role(TimestampedModel):
    """Роль в системе RBAC."""

    class Level(models.TextChoices):
        GLOBAL = "global", _("Глобальная")
        DEPARTMENT = "department", _("Департамент")
        PERSONAL = "personal", _("Персональная")

    name = models.CharField(_("название"), max_length=100)
    code = models.CharField(_("код"), max_length=50, unique=True)
    description = models.TextField(_("описание"), blank=True)
    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        verbose_name=_("разрешения"),
        blank=True,
    )
    level = models.CharField(
        _("уровень"),
        max_length=20,
        choices=Level.choices,
        default=Level.GLOBAL,
    )

    class Meta:
        verbose_name = _("роль")
        verbose_name_plural = _("роли")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class RolePermission(TimestampedModel):
    """Связь роли и разрешения."""

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
        verbose_name=_("роль"),
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="role_permissions",
        verbose_name=_("разрешение"),
    )

    class Meta:
        verbose_name = _("разрешение роли")
        verbose_name_plural = _("разрешения ролей")
        unique_together = [("role", "permission")]

    def __str__(self) -> str:
        return f"{self.role} → {self.permission}"


class UserRole(TimestampedModel):
    """Назначение роли пользователю."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_("пользователь"),
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_("роль"),
    )
    # department FK будет добавлен в фазе 2 при создании apps.departments
    # department = models.ForeignKey("departments.Department", ...)

    class Meta:
        verbose_name = _("роль пользователя")
        verbose_name_plural = _("роли пользователей")
        unique_together = [("user", "role")]

    def __str__(self) -> str:
        return f"{self.user} — {self.role}"


class OTPCode(TimestampedModel):
    """Код одноразовой верификации."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otp_codes",
        verbose_name=_("пользователь"),
    )
    code = models.CharField(_("код"), max_length=6)
    expires_at = models.DateTimeField(_("истекает"))
    is_used = models.BooleanField(_("использован"), default=False)
    attempts = models.IntegerField(_("попытки"), default=0)

    class Meta:
        verbose_name = _("OTP код")
        verbose_name_plural = _("OTP коды")

    def __str__(self) -> str:
        return f"OTP для {self.user} ({'использован' if self.is_used else 'активен'})"
