from __future__ import annotations

from rest_framework import serializers

from .models import Candidate, Interview, Vacancy


class InterviewSerializer(serializers.ModelSerializer):
    interviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            "id",
            "interview_type",
            "scheduled_at",
            "result",
            "notes",
            "duration_minutes",
            "interviewer",
            "interviewer_name",
        ]

    def get_interviewer_name(self, obj: Interview) -> str:
        return obj.interviewer.get_full_name() or obj.interviewer.email


class CandidateListSerializer(serializers.ModelSerializer):
    vacancy_title = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Candidate
        fields = [
            "id",
            "full_name",
            "first_name",
            "last_name",
            "phone",
            "email",
            "stage",
            "source",
            "vacancy_title",
            "applied_at",
        ]

    def get_vacancy_title(self, obj: Candidate) -> str:
        title = obj.vacancy.title
        if isinstance(title, dict):
            return title.get("ru") or title.get("en") or ""
        return str(title)


class CandidateDetailSerializer(CandidateListSerializer):
    interviews = InterviewSerializer(many=True, read_only=True)

    class Meta(CandidateListSerializer.Meta):
        fields = CandidateListSerializer.Meta.fields + [
            "middle_name",
            "notes",
            "resume",
            "interviews",
        ]


class CandidateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = [
            "id",
            "vacancy",
            "first_name",
            "last_name",
            "middle_name",
            "phone",
            "email",
            "resume",
            "source",
            "stage",
            "notes",
        ]


class VacancyListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.__str__", read_only=True)
    candidates_count = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = [
            "id",
            "title",
            "department_name",
            "status",
            "vacancies_count",
            "candidates_count",
            "deadline",
            "created_at",
        ]

    def get_candidates_count(self, obj: Vacancy) -> int:
        # Use annotated value if available (num_candidates), otherwise query
        if hasattr(obj, "num_candidates"):
            return obj.num_candidates  # type: ignore[return-value]
        return obj.candidates.count()


class VacancyDetailSerializer(VacancyListSerializer):
    candidates = CandidateListSerializer(many=True, read_only=True)
    position_name = serializers.SerializerMethodField()

    class Meta(VacancyListSerializer.Meta):
        fields = VacancyListSerializer.Meta.fields + [
            "requirements",
            "responsibilities",
            "position",
            "position_name",
            "candidates",
        ]

    def get_position_name(self, obj: Vacancy) -> str | None:
        if obj.position:
            return str(obj.position)
        return None


class VacancyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = [
            "id",
            "title",
            "position",
            "department",
            "requirements",
            "responsibilities",
            "status",
            "vacancies_count",
            "deadline",
        ]
