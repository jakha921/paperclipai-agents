from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.leaves.models import LeaveRequest


@receiver(post_save, sender=LeaveRequest)
def notify_on_leave_status_change(sender, instance: LeaveRequest, created: bool, **kwargs) -> None:
    """Отправить уведомление при изменении статуса заявки на отпуск."""
    from apps.notifications.services import send_from_template

    if not instance.pk:
        return

    employee = instance.employee
    user = employee.user if hasattr(employee, "user") else None
    if not user:
        return

    language = getattr(user, "language", "ru") or "ru"
    employee_name = str(employee)
    ctx = {
        "employee_name": employee_name,
        "start_date": str(instance.start_date),
        "end_date": str(instance.end_date),
    }

    if created and instance.status == LeaveRequest.Status.DRAFT:
        return

    if instance.status == LeaveRequest.Status.PENDING_HEAD:
        send_from_template(
            recipient=user,
            template_code="leave_request_created",
            context=ctx,
            language=language,
        )
    elif instance.status == LeaveRequest.Status.APPROVED:
        send_from_template(
            recipient=user,
            template_code="leave_approved",
            context=ctx,
            language=language,
        )
    elif instance.status == LeaveRequest.Status.REJECTED:
        send_from_template(
            recipient=user,
            template_code="leave_rejected",
            context=ctx,
            language=language,
        )
