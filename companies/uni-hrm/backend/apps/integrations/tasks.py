import logging

from django.utils import timezone

logger = logging.getLogger(__name__)

# Импорт celery с fallback если не настроен
try:
    from celery import shared_task

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

    def shared_task(func):  # type: ignore[no-redef]
        return func


if CELERY_AVAILABLE:

    @shared_task(bind=True, max_retries=3)
    def sync_departments_from_hemis(self):
        """Синхронизация отделов из HEMIS."""
        from . import services
        from .models import SyncLog

        log = SyncLog.objects.create(sync_type="departments", status="running")
        try:
            stats = services.sync_departments()
            log.status = "success"
            log.stats = stats
            log.completed_at = timezone.now()
            log.save(update_fields=["status", "stats", "completed_at"])
            return stats
        except Exception as exc:
            log.status = "error"
            log.error_message = str(exc)
            log.completed_at = timezone.now()
            log.save(update_fields=["status", "error_message", "completed_at"])
            raise self.retry(exc=exc, countdown=60)

    @shared_task(bind=True, max_retries=3)
    def sync_employees_from_hemis(self):
        """Синхронизация сотрудников из HEMIS."""
        from . import services
        from .models import SyncLog

        log = SyncLog.objects.create(sync_type="employees", status="running")
        try:
            stats = services.sync_employees()
            log.status = "success"
            log.stats = stats
            log.completed_at = timezone.now()
            log.save(update_fields=["status", "stats", "completed_at"])
            return stats
        except Exception as exc:
            log.status = "error"
            log.error_message = str(exc)
            log.completed_at = timezone.now()
            log.save(update_fields=["status", "error_message", "completed_at"])
            raise self.retry(exc=exc, countdown=60)

    @shared_task(bind=True)
    def sync_academic_loads_from_hemis(self, semester: str):
        """Синхронизация учебной нагрузки из HEMIS."""
        from .hemis_client import HEMISClient
        from .models import SyncLog

        log = SyncLog.objects.create(sync_type="academic", status="running")
        try:
            client = HEMISClient()
            loads = client.get_academic_loads(semester)
            log.status = "success"
            log.stats = {"loaded": len(loads)}
            log.completed_at = timezone.now()
            log.save(update_fields=["status", "stats", "completed_at"])
            return {"loaded": len(loads)}
        except Exception as exc:
            log.status = "error"
            log.error_message = str(exc)
            log.completed_at = timezone.now()
            log.save(update_fields=["status", "error_message", "completed_at"])

    @shared_task
    def run_full_sync():
        """Запустить полную синхронизацию всех данных."""
        from . import services
        from .models import SyncLog

        log = SyncLog.objects.create(sync_type="full", status="running")
        try:
            dept_stats = services.sync_departments()
            emp_stats = services.sync_employees()
            log.status = "success"
            log.stats = {"departments": dept_stats, "employees": emp_stats}
            log.completed_at = timezone.now()
            log.save(update_fields=["status", "stats", "completed_at"])
        except Exception as exc:
            log.status = "error"
            log.error_message = str(exc)
            log.completed_at = timezone.now()
            log.save(update_fields=["status", "error_message", "completed_at"])

else:
    # Синхронные версии для случая без Celery
    def sync_departments_from_hemis():  # type: ignore[no-redef]
        from . import services
        from .models import SyncLog

        log = SyncLog.objects.create(sync_type="departments", status="running")
        stats = services.sync_departments()
        log.status = "success"
        log.stats = stats
        log.completed_at = timezone.now()
        log.save(update_fields=["status", "stats", "completed_at"])
        return stats

    def sync_employees_from_hemis():  # type: ignore[no-redef]
        from . import services
        from .models import SyncLog

        log = SyncLog.objects.create(sync_type="employees", status="running")
        stats = services.sync_employees()
        log.status = "success"
        log.stats = stats
        log.completed_at = timezone.now()
        log.save(update_fields=["status", "stats", "completed_at"])
        return stats

    def run_full_sync():  # type: ignore[no-redef]
        from . import services
        from .models import SyncLog

        log = SyncLog.objects.create(sync_type="full", status="running")
        dept_stats = services.sync_departments()
        emp_stats = services.sync_employees()
        log.status = "success"
        log.stats = {"departments": dept_stats, "employees": emp_stats}
        log.completed_at = timezone.now()
        log.save(update_fields=["status", "stats", "completed_at"])
