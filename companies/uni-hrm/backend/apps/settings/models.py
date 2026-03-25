import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel

SETTINGS_UUID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class SystemSettings(TimestampedModel):
    """Singleton model — one record for the entire system."""

    site_name = models.CharField(max_length=200, default="Uni-HRM", verbose_name=_("Site Name"))
    site_url = models.CharField(max_length=200, blank=True, verbose_name=_("Site URL"))
    working_hours_start = models.TimeField(default="09:00", verbose_name=_("Working Hours Start"))
    working_hours_end = models.TimeField(default="18:00", verbose_name=_("Working Hours End"))
    working_days = models.JSONField(default=list, verbose_name=_("Working Days"))
    annual_leave_days = models.PositiveIntegerField(default=28, verbose_name=_("Annual Leave Days"))
    sick_leave_days = models.PositiveIntegerField(default=14, verbose_name=_("Sick Leave Days"))
    currency = models.CharField(max_length=10, default="UZS", verbose_name=_("Currency"))
    timezone = models.CharField(max_length=50, default="Asia/Tashkent", verbose_name=_("Timezone"))
    smtp_host = models.CharField(max_length=200, blank=True, verbose_name=_("SMTP Host"))
    smtp_port = models.PositiveIntegerField(default=587, verbose_name=_("SMTP Port"))
    smtp_use_tls = models.BooleanField(default=True, verbose_name=_("SMTP Use TLS"))
    smtp_username = models.CharField(max_length=200, blank=True, verbose_name=_("SMTP Username"))
    from_email = models.CharField(max_length=200, blank=True, verbose_name=_("From Email"))

    class Meta:
        verbose_name = _("System Settings")
        verbose_name_plural = _("System Settings")

    def __str__(self) -> str:
        return self.site_name

    @classmethod
    def get_settings(cls) -> "SystemSettings":
        obj, _ = cls.objects.get_or_create(pk=SETTINGS_UUID)
        return obj
