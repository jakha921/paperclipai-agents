import django_filters
from django.db.models import Q

from .models import Employee


class EmployeeFilter(django_filters.FilterSet):
    hire_date_from = django_filters.DateFilter(field_name="hire_date", lookup_expr="gte")
    hire_date_to = django_filters.DateFilter(field_name="hire_date", lookup_expr="lte")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Employee
        fields = {
            "department": ["exact"],
            "position": ["exact"],
            "status": ["exact"],
            "contract_type": ["exact"],
            "gender": ["exact"],
        }

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(middle_name__icontains=value)
            | Q(employee_number__icontains=value)
        )
