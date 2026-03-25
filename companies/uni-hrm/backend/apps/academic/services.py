from __future__ import annotations

from apps.academic.models import AcademicLoad


def calculate_total_load(employee_id: int, academic_year: str) -> dict:
    """Рассчитать общую учебную нагрузку преподавателя за учебный год.

    Возвращает total_hours, by_semester, by_subject, exceeds_limit (лимит=900).
    """
    loads = AcademicLoad.objects.filter(
        employee_id=employee_id,
        academic_year=academic_year,
    ).select_related("subject")

    total = 0
    by_semester: dict[int, int] = {1: 0, 2: 0}
    by_subject: dict[str, int] = {}

    for load in loads:
        hours = load.total_hours
        total += hours
        by_semester[load.semester] = by_semester.get(load.semester, 0) + hours
        subject_name = load.subject.name.get("ru", str(load.subject.id))
        by_subject[subject_name] = by_subject.get(subject_name, 0) + hours

    return {
        "total_hours": total,
        "by_semester": by_semester,
        "by_subject": by_subject,
        "exceeds_limit": total > 900,
    }
