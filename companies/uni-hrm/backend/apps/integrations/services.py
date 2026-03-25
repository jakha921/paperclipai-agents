import logging

from django.utils import timezone

from .hemis_client import HEMISClient
from .models import HEMISMapping, SyncConflict

logger = logging.getLogger(__name__)


def sync_departments() -> dict:
    """Синхронизировать отделы из HEMIS."""
    client = HEMISClient()
    stats = {"created": 0, "updated": 0, "errors": 0}

    try:
        hemis_departments = client.get_departments()
    except Exception as exc:
        logger.error("Failed to fetch departments from HEMIS: %s", exc)
        return {"created": 0, "updated": 0, "errors": 1}

    try:
        from apps.departments.models import Department

        for dept_data in hemis_departments:
            hemis_id = str(dept_data.get("id", ""))
            name = dept_data.get("name", "")

            dept = Department.objects.filter(name=name).first()
            if not dept:
                try:
                    dept = Department.objects.create(name=name)
                    stats["created"] += 1
                except Exception:
                    stats["errors"] += 1
                    continue
            else:
                stats["updated"] += 1

            HEMISMapping.objects.update_or_create(
                content_type="department",
                hemis_id=hemis_id,
                defaults={
                    "local_id": str(dept.id),
                    "sync_status": "success",
                    "last_synced_at": timezone.now(),
                },
            )
    except Exception as exc:
        logger.error("Department sync error: %s", exc)
        stats["errors"] += 1

    return stats


def sync_employees() -> dict:
    """Синхронизировать сотрудников из HEMIS."""
    client = HEMISClient()
    stats = {"created": 0, "updated": 0, "errors": 0}

    try:
        hemis_employees = client.get_employees()
    except Exception as exc:
        logger.error("Failed to fetch employees from HEMIS: %s", exc)
        return {"created": 0, "updated": 0, "errors": 1}

    try:
        from apps.accounts.models import Employee

        for emp_data in hemis_employees:
            hemis_id = str(emp_data.get("id", ""))
            pinfl = emp_data.get("pinfl", "")

            local_employee = None
            if pinfl and hasattr(Employee, "pinfl"):
                local_employee = Employee.objects.filter(pinfl=pinfl).first()

            if local_employee:
                local_name = str(local_employee)
                hemis_name = emp_data.get("name", "")
                if local_name != hemis_name and hemis_name:
                    mapping, _ = HEMISMapping.objects.get_or_create(
                        content_type="employee",
                        hemis_id=hemis_id,
                        defaults={"local_id": str(local_employee.id), "sync_status": "success"},
                    )
                    SyncConflict.objects.get_or_create(
                        mapping=mapping,
                        field_name="name",
                        defaults={
                            "local_value": local_name,
                            "hemis_value": hemis_name,
                        },
                    )
                stats["updated"] += 1
            else:
                stats["created"] += 1

    except Exception as exc:
        logger.error("Employee sync error: %s", exc)
        stats["errors"] += 1

    return stats
