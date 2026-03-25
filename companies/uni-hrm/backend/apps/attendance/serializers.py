from __future__ import annotations

from rest_framework import serializers

from apps.attendance.models import AttendanceRecord, EmployeeSchedule, TimeSheet, WorkSchedule


class WorkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSchedule
        fields = [
            "id",
            "name",
            "schedule_type",
            "work_start",
            "work_end",
            "break_start",
            "break_end",
            "working_days",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class EmployeeScheduleSerializer(serializers.ModelSerializer):
    schedule = WorkScheduleSerializer(read_only=True)
    schedule_id = serializers.PrimaryKeyRelatedField(
        queryset=WorkSchedule.objects.all(), source="schedule", write_only=True
    )

    class Meta:
        model = EmployeeSchedule
        fields = [
            "id",
            "employee",
            "schedule",
            "schedule_id",
            "effective_from",
            "effective_to",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = [
            "id",
            "employee",
            "date",
            "check_in",
            "check_out",
            "status",
            "worked_hours",
            "overtime_hours",
            "source",
            "note",
            "created_at",
        ]
        read_only_fields = ["worked_hours", "overtime_hours", "created_at"]

    def validate(self, attrs: dict) -> dict:
        check_in = attrs.get("check_in")
        check_out = attrs.get("check_out")
        if check_in and check_out and check_in >= check_out:
            raise serializers.ValidationError(
                {"check_out": "Время ухода должно быть позже прихода"}
            )
        return attrs


class BulkAttendanceSerializer(serializers.Serializer):
    records = AttendanceRecordSerializer(many=True)


class TimeSheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSheet
        fields = [
            "id",
            "employee",
            "month",
            "year",
            "total_working_days",
            "days_present",
            "days_absent",
            "days_late",
            "days_on_leave",
            "total_hours",
            "overtime_hours",
            "status",
            "approved_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
