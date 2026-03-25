from __future__ import annotations

import django_filters

from apps.payroll.models import EmployeeSalary, Payroll


class PayrollFilter(django_filters.FilterSet):
    month = django_filters.NumberFilter()
    year = django_filters.NumberFilter()
    status = django_filters.CharFilter()
    employee = django_filters.UUIDFilter(field_name="employee__id")

    class Meta:
        model = Payroll
        fields = ["month", "year", "status", "employee"]


class EmployeeSalaryFilter(django_filters.FilterSet):
    employee = django_filters.UUIDFilter(field_name="employee__id")
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = EmployeeSalary
        fields = ["employee", "is_active"]
