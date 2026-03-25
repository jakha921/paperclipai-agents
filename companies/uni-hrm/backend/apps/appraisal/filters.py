import django_filters

from apps.appraisal.models import EmployeeAppraisal, TrainingRecord


class EmployeeAppraisalFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    employee = django_filters.UUIDFilter(field_name="employee__id")
    cycle = django_filters.UUIDFilter(field_name="cycle__id")

    class Meta:
        model = EmployeeAppraisal
        fields = ["status", "employee", "cycle"]


class TrainingRecordFilter(django_filters.FilterSet):
    employee = django_filters.UUIDFilter(field_name="employee__id")
    program = django_filters.UUIDFilter(field_name="program__id")
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = TrainingRecord
        fields = ["employee", "program", "status"]
