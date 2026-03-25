import django_filters

from apps.academic.models import AcademicLoad, EmployeeAcademic, PositionContest, Subject


class EmployeeAcademicFilter(django_filters.FilterSet):
    class Meta:
        model = EmployeeAcademic
        fields = ["degree", "title"]


class SubjectFilter(django_filters.FilterSet):
    class Meta:
        model = Subject
        fields = ["department", "is_active"]


class AcademicLoadFilter(django_filters.FilterSet):
    class Meta:
        model = AcademicLoad
        fields = ["employee", "academic_year", "semester"]


class PositionContestFilter(django_filters.FilterSet):
    class Meta:
        model = PositionContest
        fields = ["department", "status"]
