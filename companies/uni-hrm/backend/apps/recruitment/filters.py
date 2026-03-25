from __future__ import annotations

import django_filters

from .models import Candidate, Interview, Vacancy


class VacancyFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    department = django_filters.UUIDFilter(field_name="department_id")

    class Meta:
        model = Vacancy
        fields = ["status", "department"]


class CandidateFilter(django_filters.FilterSet):
    vacancy = django_filters.UUIDFilter(field_name="vacancy_id")
    stage = django_filters.CharFilter(field_name="stage")
    source = django_filters.CharFilter(field_name="source")

    class Meta:
        model = Candidate
        fields = ["vacancy", "stage", "source"]


class InterviewFilter(django_filters.FilterSet):
    candidate = django_filters.UUIDFilter(field_name="candidate_id")
    interview_type = django_filters.CharFilter(field_name="interview_type")
    result = django_filters.CharFilter(field_name="result")

    class Meta:
        model = Interview
        fields = ["candidate", "interview_type", "result"]
