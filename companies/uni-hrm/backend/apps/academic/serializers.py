from __future__ import annotations

from rest_framework import serializers

from apps.academic.models import (
    AcademicDegree,
    AcademicLoad,
    AcademicTitle,
    EmployeeAcademic,
    PositionContest,
    Subject,
)


class AcademicDegreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicDegree
        fields = ["id", "name", "code", "country", "created_at"]
        read_only_fields = ["created_at"]


class AcademicTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicTitle
        fields = ["id", "name", "code", "created_at"]
        read_only_fields = ["created_at"]


class EmployeeAcademicSerializer(serializers.ModelSerializer):
    degree = AcademicDegreeSerializer(read_only=True)
    degree_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicDegree.objects.all(),
        source="degree",
        write_only=True,
        required=False,
        allow_null=True,
    )
    title = AcademicTitleSerializer(read_only=True)
    title_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicTitle.objects.all(),
        source="title",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = EmployeeAcademic
        fields = [
            "id",
            "employee",
            "degree",
            "degree_id",
            "title",
            "title_id",
            "specialization",
            "dissertation_topic",
            "diploma_number",
            "awarded_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [
            "id",
            "name",
            "code",
            "department",
            "credits",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class AcademicLoadSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        source="subject",
        write_only=True,
    )
    total_hours = serializers.ReadOnlyField()

    class Meta:
        model = AcademicLoad
        fields = [
            "id",
            "employee",
            "subject",
            "subject_id",
            "academic_year",
            "semester",
            "lecture_hours",
            "seminar_hours",
            "lab_hours",
            "load_type",
            "total_hours",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class AcademicLoadSummarySerializer(serializers.Serializer):
    total_hours = serializers.IntegerField()
    by_semester = serializers.DictField(child=serializers.IntegerField())
    by_subject = serializers.DictField(child=serializers.IntegerField())
    exceeds_limit = serializers.BooleanField()


class PositionContestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionContest
        fields = [
            "id",
            "department",
            "position",
            "requirements",
            "application_deadline",
            "status",
            "winner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "winner", "created_at", "updated_at"]
