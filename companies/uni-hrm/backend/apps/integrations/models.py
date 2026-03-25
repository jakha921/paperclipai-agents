from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class HEMISMapping(TimestampedModel):
    """Маппинг между локальными объектами и HEMIS ID."""

    class ContentType(models.TextChoices):
        DEPARTMENT = "department", "Department"
        EMPLOYEE = "employee", "Employee"
        SUBJECT = "subject", "Subject"

    class SyncStatus(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"
        PENDING = "pending", "Pending"

    content_type = models.CharField(
        max_length=20, choices=ContentType.choices, verbose_name=_("Content Type")
    )
    local_id = models.CharField(max_length=50, verbose_name=_("Local ID"))
    hemis_id = models.CharField(max_length=50, verbose_name=_("HEMIS ID"))
    last_synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=10, choices=SyncStatus.choices, default=SyncStatus.PENDING
    )

    class Meta:
        verbose_name = _("HEMIS Mapping")
        verbose_name_plural = _("HEMIS Mappings")
        unique_together = [("content_type", "local_id")]

    def __str__(self) -> str:
        return f"{self.content_type}: {self.local_id} -> {self.hemis_id}"


class SyncLog(TimestampedModel):
    """Лог операций синхронизации с HEMIS."""

    class SyncType(models.TextChoices):
        DEPARTMENTS = "departments", "Departments"
        EMPLOYEES = "employees", "Employees"
        ACADEMIC = "academic", "Academic"
        FULL = "full", "Full"

    class Status(models.TextChoices):
        RUNNING = "running", "Running"
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    sync_type = models.CharField(
        max_length=15, choices=SyncType.choices, verbose_name=_("Sync Type")
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.RUNNING)
    stats = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Sync Log")
        verbose_name_plural = _("Sync Logs")
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.sync_type} -- {self.status} ({self.started_at.date()})"


class SyncConflict(TimestampedModel):
    """Конфликты при синхронизации данных."""

    mapping = models.ForeignKey(HEMISMapping, on_delete=models.CASCADE, related_name="conflicts")
    field_name = models.CharField(max_length=50)
    local_value = models.TextField()
    hemis_value = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolution = models.CharField(max_length=10, blank=True)  # "local" or "hemis"
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_conflicts",
    )

    class Meta:
        verbose_name = _("Sync Conflict")
        verbose_name_plural = _("Sync Conflicts")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.mapping} -- {self.field_name}"
