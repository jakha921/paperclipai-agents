from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class DocumentTemplate(TimestampedModel):
    """Шаблон документа (приказы, справки, договоры)."""

    class OutputFormat(models.TextChoices):
        PDF = "pdf", "PDF"
        DOCX = "docx", "DOCX"

    name = models.CharField(max_length=200, verbose_name=_("Name"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Code"))
    template_html = models.TextField(verbose_name=_("Template HTML"))
    variables_schema = models.JSONField(default=dict)
    output_format = models.CharField(
        max_length=5, choices=OutputFormat.choices, default=OutputFormat.PDF
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Document Template")
        verbose_name_plural = _("Document Templates")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class GeneratedDocument(TimestampedModel):
    """Сгенерированный документ."""

    template = models.ForeignKey(
        DocumentTemplate, on_delete=models.PROTECT, related_name="documents"
    )
    employee = models.ForeignKey(
        "departments.Employee", on_delete=models.CASCADE, related_name="documents"
    )
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to="documents/%Y/%m/", blank=True)
    data = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Generated Document")
        verbose_name_plural = _("Generated Documents")
        ordering = ["-generated_at"]

    def __str__(self) -> str:
        return f"{self.template.name} — {self.employee}"
