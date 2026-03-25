from __future__ import annotations

from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.leaves.models import LeaveAllocation, LeaveRequest


@receiver(post_save, sender=LeaveRequest)
def update_allocation_on_status_change(
    sender, instance: LeaveRequest, created: bool, **kwargs
) -> None:
    """Update used_days in LeaveAllocation on any status change."""
    if not instance.pk:
        return

    year = instance.start_date.year
    try:
        allocation = LeaveAllocation.objects.get(
            employee=instance.employee,
            leave_type=instance.leave_type,
            year=year,
        )
    except LeaveAllocation.DoesNotExist:
        return

    # Recalculate used_days from all approved requests
    total = (
        LeaveRequest.objects.filter(
            employee=instance.employee,
            leave_type=instance.leave_type,
            start_date__year=year,
            status=LeaveRequest.Status.APPROVED,
        ).aggregate(total=Sum("days_count"))["total"]
        or 0
    )
    allocation.used_days = total
    allocation.save(update_fields=["used_days", "updated_at"])
