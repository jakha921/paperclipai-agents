import django_filters

from apps.attendance.models import AttendanceRecord, TimeSheet


class AttendanceRecordFilter(django_filters.FilterSet):
    employee = django_filters.UUIDFilter(field_name="employee__id")
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    status = django_filters.CharFilter(field_name="status")
    department = django_filters.UUIDFilter(field_name="employee__department__id")

    class Meta:
        model = AttendanceRecord
        fields = ["employee", "status", "date_from", "date_to", "department"]


class TimeSheetFilter(django_filters.FilterSet):
    employee = django_filters.UUIDFilter(field_name="employee__id")
    month = django_filters.NumberFilter(field_name="month")
    year = django_filters.NumberFilter(field_name="year")
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = TimeSheet
        fields = ["employee", "month", "year", "status"]
