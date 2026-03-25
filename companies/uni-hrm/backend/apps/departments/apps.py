from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DepartmentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.departments"
    verbose_name = _("Подразделения и сотрудники")

    def ready(self) -> None:
        import apps.departments.signals  # noqa: F401
