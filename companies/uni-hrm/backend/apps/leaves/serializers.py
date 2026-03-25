from __future__ import annotations

from datetime import date

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.leaves.models import LeaveAllocation, LeaveRequest, LeaveType, PublicHoliday
from apps.leaves.services import calculate_working_days


class PublicHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicHoliday
        fields = ["id", "date", "name", "is_working_day", "created_at"]
        read_only_fields = ["created_at"]


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = [
            "id",
            "name",
            "code",
            "days_per_year",
            "is_paid",
            "requires_document",
            "applicable_categories",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class LeaveAllocationSerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer(read_only=True)
    leave_type_id = serializers.PrimaryKeyRelatedField(
        queryset=LeaveType.objects.all(), source="leave_type", write_only=True
    )
    remaining_days = serializers.ReadOnlyField()

    class Meta:
        model = LeaveAllocation
        fields = [
            "id",
            "employee",
            "leave_type",
            "leave_type_id",
            "year",
            "total_days",
            "used_days",
            "carry_over_days",
            "remaining_days",
            "created_at",
        ]
        read_only_fields = ["used_days", "created_at"]


class LeaveRequestSerializer(serializers.ModelSerializer):
    leave_type = LeaveTypeSerializer(read_only=True)
    leave_type_id = serializers.PrimaryKeyRelatedField(
        queryset=LeaveType.objects.all(), source="leave_type", write_only=True
    )
    days_count = serializers.ReadOnlyField()

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "leave_type",
            "leave_type_id",
            "start_date",
            "end_date",
            "days_count",
            "reason",
            "status",
            "approved_by",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "days_count",
            "status",
            "approved_by",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs: dict) -> dict:
        start_date: date = attrs.get("start_date")
        end_date: date = attrs.get("end_date")
        leave_type: LeaveType = attrs.get("leave_type")
        request = self.context.get("request")

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                {"end_date": _("Дата окончания должна быть позже даты начала")}
            )

        if start_date and end_date:
            attrs["days_count"] = calculate_working_days(start_date, end_date)

        # Check allocation balance
        if leave_type and start_date and request:
            employee = getattr(request.user, "employee", None)
            if employee:
                year = start_date.year
                allocation = LeaveAllocation.objects.filter(
                    employee=employee, leave_type=leave_type, year=year
                ).first()
                if allocation:
                    days = attrs.get("days_count", 0)
                    if days > allocation.remaining_days:
                        raise serializers.ValidationError(
                            {
                                "days_count": _(
                                    "Недостаточно дней отпуска."
                                    f" Доступно: {allocation.remaining_days}"
                                )
                            }
                        )
                # Check overlaps
                overlapping = LeaveRequest.objects.filter(
                    employee=employee,
                    status__in=[
                        LeaveRequest.Status.PENDING_HEAD,
                        LeaveRequest.Status.PENDING_HR,
                        LeaveRequest.Status.APPROVED,
                    ],
                    start_date__lte=end_date,
                    end_date__gte=start_date,
                )
                if self.instance:
                    overlapping = overlapping.exclude(pk=self.instance.pk)
                if overlapping.exists():
                    raise serializers.ValidationError(
                        _("Период пересекается с существующей заявкой")
                    )

        return attrs

    def create(self, validated_data: dict) -> LeaveRequest:
        request = self.context.get("request")
        if request and hasattr(request.user, "employee"):
            validated_data["employee"] = request.user.employee
        start_date = validated_data.get("start_date")
        end_date = validated_data.get("end_date")
        if start_date and end_date:
            validated_data["days_count"] = calculate_working_days(start_date, end_date)
        return super().create(validated_data)


class LeaveBalanceSerializer(serializers.Serializer):
    leave_type = LeaveTypeSerializer()
    total_days = serializers.IntegerField()
    used_days = serializers.IntegerField()
    carry_over_days = serializers.IntegerField()
    remaining_days = serializers.IntegerField()


class LeaveCalendarEventSerializer(serializers.Serializer):
    employee_name = serializers.CharField()
    leave_type = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    status = serializers.CharField()
