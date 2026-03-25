from datetime import date, timedelta

from django.db.models import Avg, Count
from django.utils import timezone


def get_dashboard_stats() -> dict:
    """Статистика для HR Dashboard."""
    from apps.departments.models import Employee

    today = timezone.now().date()
    first_of_month = today.replace(day=1)

    total_employees = Employee.objects.filter(is_deleted=False).count()

    stats = {
        "total_employees": total_employees,
        "total_departments": 0,
        "open_vacancies": 0,
        "pending_leaves": 0,
        "total_payroll_last_month": 0,
        "avg_salary": 0,
        "new_hires_this_month": 0,
    }

    try:
        from apps.departments.models import Department

        stats["total_departments"] = Department.objects.filter(is_active=True).count()
    except Exception:
        pass

    try:
        from apps.recruitment.models import Vacancy

        stats["open_vacancies"] = Vacancy.objects.filter(status="OPEN").count()
    except Exception:
        pass

    try:
        from apps.leaves.models import LeaveRequest

        stats["pending_leaves"] = LeaveRequest.objects.filter(
            status__in=["PENDING_HEAD", "PENDING_HR"]
        ).count()
    except Exception:
        pass

    try:
        from apps.payroll.models import EmployeeSalary

        result = EmployeeSalary.objects.filter(is_active=True).aggregate(avg=Avg("base_salary"))
        stats["avg_salary"] = float(result["avg"] or 0)
    except Exception:
        pass

    try:
        stats["new_hires_this_month"] = Employee.objects.filter(
            is_deleted=False, hire_date__gte=first_of_month
        ).count()
    except Exception:
        pass

    return stats


def get_turnover_stats(months: int = 12) -> list:
    """Статистика текучести по месяцам."""
    from apps.departments.models import Employee

    result = []
    today = date.today()

    for i in range(months - 1, -1, -1):
        month_date = (today.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        month_str = month_date.strftime("%Y-%m")

        hired = Employee.objects.filter(
            hire_date__year=month_date.year, hire_date__month=month_date.month
        ).count()

        dismissed = Employee.objects.filter(
            status="DISMISSED",
            updated_at__year=month_date.year,
            updated_at__month=month_date.month,
        ).count()

        total = Employee.objects.filter(hire_date__lte=month_date).count()
        turnover = round(dismissed / total * 100, 2) if total > 0 else 0.0

        result.append(
            {
                "month": month_str,
                "hired_count": hired,
                "dismissed_count": dismissed,
                "turnover_rate": turnover,
            }
        )

    return result


def get_department_stats() -> list:
    """Статистика по отделам."""
    from apps.departments.models import Department

    departments = Department.objects.filter(is_active=True).annotate(
        employee_count=Count("employees")
    )

    result = []
    for dept in departments:
        open_vacancies = 0
        try:
            from apps.recruitment.models import Vacancy

            open_vacancies = Vacancy.objects.filter(department=dept, status="OPEN").count()
        except Exception:
            pass

        result.append(
            {
                "id": str(dept.id),
                "name": str(dept),
                "employee_count": dept.employee_count,
                "open_vacancies": open_vacancies,
            }
        )
    return result


def get_demographics() -> dict:
    """Демографическая статистика."""
    from apps.departments.models import Employee

    total = Employee.objects.filter(is_deleted=False).count()

    gender_qs = (
        Employee.objects.filter(is_deleted=False).values("gender").annotate(count=Count("id"))
    )
    gender_distribution = {g["gender"]: g["count"] for g in gender_qs}

    return {
        "total": total,
        "gender_distribution": gender_distribution,
        "age_groups": {},
        "education_levels": {},
        "experience_groups": {},
    }
