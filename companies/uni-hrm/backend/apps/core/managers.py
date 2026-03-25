from django.db import models


class ActiveManager(models.Manager):
    """Менеджер, исключающий мягко удалённые записи."""

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_deleted=False)
