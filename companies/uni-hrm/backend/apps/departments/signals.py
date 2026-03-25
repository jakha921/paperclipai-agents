from __future__ import annotations

from datetime import date

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_save, sender="departments.Employee")
def generate_employee_number(sender, instance, created: bool, **kwargs) -> None:
    """Автогенерация табельного номера при создании."""
    if created and not instance.employee_number:
        hire = instance.hire_date
        if isinstance(hire, str):
            hire = date.fromisoformat(hire)
        date_str = hire.strftime("%Y%m%d") if hire else timezone.now().strftime("%Y%m%d")
        seq = instance.__class__.objects.filter(
            employee_number__startswith=f"EMP-{date_str}"
        ).count()
        instance.employee_number = f"EMP-{date_str}-{seq + 1:04d}"
        instance.__class__.objects.filter(pk=instance.pk).update(
            employee_number=instance.employee_number
        )


@receiver(post_save, sender="departments.Employee")
def create_employment_history(sender, instance, created: bool, **kwargs) -> None:
    """Создание записи истории при найме."""
    from apps.departments.models import EmploymentHistory

    if created:
        EmploymentHistory.objects.create(
            employee=instance,
            department=instance.department,
            position=instance.position,
            start_date=instance.hire_date,
            order_number="",
            order_date=instance.hire_date,
            change_reason=EmploymentHistory.ChangeReason.HIRED,
        )
