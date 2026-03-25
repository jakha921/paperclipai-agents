from __future__ import annotations

from rest_framework import serializers

from apps.payroll.models import EmployeeSalary, Payroll, TaxConfiguration


class TaxConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxConfiguration
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class EmployeeSalarySerializer(serializers.ModelSerializer):
    gross_monthly = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = EmployeeSalary
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = Payroll
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "gross_salary",
            "net_salary",
            "total_deductions",
            "ndfl",
            "inps_employee",
            "employer_social_tax",
            "employer_inps",
        ]

    def get_employee_name(self, obj: Payroll) -> str:
        return str(obj.employee)


class PayslipSerializer(serializers.ModelSerializer):
    """Детальный расчётный лист."""

    employee_name = serializers.SerializerMethodField()
    employee_position = serializers.SerializerMethodField()

    class Meta:
        model = Payroll
        fields = "__all__"

    def get_employee_name(self, obj: Payroll) -> str:
        return str(obj.employee)

    def get_employee_position(self, obj: Payroll) -> str:
        if hasattr(obj.employee, "position") and obj.employee.position:
            return str(obj.employee.position)
        return ""
