import django_filters

from apps.leaves.models import LeaveRequest


class LeaveRequestFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    employee = django_filters.UUIDFilter(field_name="employee__id")
    leave_type = django_filters.UUIDFilter(field_name="leave_type__id")
    start_date = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="end_date", lookup_expr="lte")

    class Meta:
        model = LeaveRequest
        fields = ["status", "employee", "leave_type", "start_date", "end_date"]
