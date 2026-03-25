from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class NotificationTemplate(TimestampedModel):
    """Шаблон уведомления."""

    code = models.CharField(_("код"), max_length=50, unique=True)
    name = models.CharField(_("название"), max_length=255)
    title = models.JSONField(_("заголовок"), default=dict, help_text="{'ru': '...', 'uz': '...'}")
    body = models.JSONField(_("тело"), default=dict, help_text="{'ru': '...', 'uz': '...'}")
    channels = models.JSONField(
        _("каналы"),
        default=list,
        help_text='["in_app", "email", "telegram"]',
    )

    class Meta:
        verbose_name = _("Шаблон уведомления")
        verbose_name_plural = _("Шаблоны уведомлений")
        ordering = ["code"]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class Notification(TimestampedModel):
    """Уведомление пользователю."""

    class Channel(models.TextChoices):
        IN_APP = "in_app", _("В приложении")
        EMAIL = "email", _("Email")
        TELEGRAM = "telegram", _("Telegram")

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Получатель"),
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name=_("Шаблон"),
    )
    title = models.CharField(_("заголовок"), max_length=255)
    message = models.TextField(_("сообщение"))
    channel = models.CharField(
        _("канал"),
        max_length=10,
        choices=Channel.choices,
        default=Channel.IN_APP,
    )
    is_read = models.BooleanField(_("прочитано"), default=False)
    read_at = models.DateTimeField(_("прочитано в"), null=True, blank=True)
    data = models.JSONField(_("данные"), default=dict, blank=True)

    class Meta:
        verbose_name = _("Уведомление")
        verbose_name_plural = _("Уведомления")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.recipient} — {self.title}"
