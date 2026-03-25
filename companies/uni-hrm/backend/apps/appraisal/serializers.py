from __future__ import annotations

from rest_framework import serializers

from apps.appraisal.models import (
    AppraisalCycle,
    AppraisalScore,
    EmployeeAppraisal,
    KPIIndicator,
    TrainingProgram,
    TrainingRecord,
)


class AppraisalCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppraisalCycle
        fields = [
            "id",
            "name",
            "start_date",
            "end_date",
            "status",
            "applicable_departments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class KPIIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = KPIIndicator
        fields = [
            "id",
            "name",
            "description",
            "category",
            "weight",
            "max_score",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class AppraisalScoreSerializer(serializers.ModelSerializer):
    kpi_detail = KPIIndicatorSerializer(source="kpi", read_only=True)

    class Meta:
        model = AppraisalScore
        fields = [
            "id",
            "appraisal",
            "kpi",
            "kpi_detail",
            "self_score",
            "manager_score",
            "final_score",
            "comment",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class EmployeeAppraisalSerializer(serializers.ModelSerializer):
    scores = AppraisalScoreSerializer(many=True, read_only=True)

    class Meta:
        model = EmployeeAppraisal
        fields = [
            "id",
            "cycle",
            "employee",
            "reviewer",
            "status",
            "overall_score",
            "comments",
            "reviewed_at",
            "scores",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "overall_score",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]


class TrainingProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingProgram
        fields = [
            "id",
            "name",
            "description",
            "provider",
            "training_type",
            "duration_hours",
            "cost",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class TrainingRecordSerializer(serializers.ModelSerializer):
    program_detail = TrainingProgramSerializer(source="program", read_only=True)

    class Meta:
        model = TrainingRecord
        fields = [
            "id",
            "employee",
            "program",
            "program_detail",
            "start_date",
            "end_date",
            "status",
            "certificate_number",
            "score",
            "created_at",
        ]
        read_only_fields = ["created_at"]
