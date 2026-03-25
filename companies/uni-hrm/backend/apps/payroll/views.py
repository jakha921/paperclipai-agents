from __future__ import annotations

from datetime import date

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.payroll.filters import EmployeeSalaryFilter, PayrollFilter
from apps.payroll.models import EmployeeSalary, Payroll, TaxConfiguration
from apps.payroll.serializers import (
    EmployeeSalarySerializer,
    PayrollSerializer,
    PayslipSerializer,
    TaxConfigurationSerializer,
)
from apps.payroll.services import calculate_payroll


class TaxConfigurationViewSet(viewsets.ModelViewSet):
    """CRUD для налоговых конфигураций."""

    queryset = TaxConfiguration.objects.all()
    serializer_class = TaxConfigurationSerializer
    permission_classes = [IsAuthenticated]


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    """CRUD для зарплат сотрудников."""

    queryset = EmployeeSalary.objects.select_related("employee").all()
    serializer_class = EmployeeSalarySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeSalaryFilter

    @action(detail=False, methods=["get"], url_path="current")
    def current(self, request):
        """Текущая (активная) зарплата сотрудника."""
        employee_id = request.query_params.get("employee")
        if not employee_id:
            return Response(
                {"detail": "employee parameter required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        salary = (
            EmployeeSalary.objects.filter(
                employee__id=employee_id,
                is_active=True,
            )
            .order_by("-effective_from")
            .first()
        )
        if not salary:
            return Response(
                {"detail": "No active salary found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(EmployeeSalarySerializer(salary).data)


class PayrollViewSet(viewsets.ModelViewSet):
    """Расчётные листы."""

    queryset = Payroll.objects.select_related("employee", "tax_config", "approved_by").all()
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = PayrollFilter

    @action(detail=True, methods=["post"])
    def calculate(self, request, pk=None):
        """Пересчитать Payroll."""
        payroll = self.get_object()
        try:
            updated = calculate_payroll(payroll.employee, payroll.month, payroll.year)
            return Response(PayrollSerializer(updated).data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="bulk_calculate")
    def bulk_calculate(self, request):
        """Рассчитать зарплату для всех активных сотрудников за месяц."""
        month = request.data.get("month")
        year = request.data.get("year")
        if not month or not year:
            return Response(
                {"detail": "month and year required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        from apps.departments.models import Employee

        employees = Employee.objects.filter(status=Employee.Status.ACTIVE, is_deleted=False)
        results = []
        errors = []
        for emp in employees:
            try:
                p = calculate_payroll(emp, int(month), int(year))
                results.append(
                    {
                        "employee": str(emp),
                        "payroll_id": str(p.pk),
                        "net_salary": str(p.net_salary),
                    }
                )
            except ValueError as e:
                errors.append({"employee": str(emp), "error": str(e)})
        return Response(
            {
                "calculated": len(results),
                "errors": len(errors),
                "results": results,
                "error_details": errors,
            }
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """CALCULATED -> APPROVED."""
        payroll = self.get_object()
        if payroll.status != Payroll.Status.CALCULATED:
            return Response(
                {"detail": "Only CALCULATED payrolls can be approved"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payroll.status = Payroll.Status.APPROVED
        payroll.approved_by = request.user
        payroll.save(update_fields=["status", "approved_by", "updated_at"])
        return Response(PayrollSerializer(payroll).data)

    @action(detail=True, methods=["post"], url_path="mark_paid")
    def mark_paid(self, request, pk=None):
        """APPROVED -> PAID."""
        payroll = self.get_object()
        if payroll.status != Payroll.Status.APPROVED:
            return Response(
                {"detail": "Only APPROVED payrolls can be marked as paid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payroll.status = Payroll.Status.PAID
        payroll.paid_date = request.data.get("paid_date") or date.today()
        payroll.save(update_fields=["status", "paid_date", "updated_at"])
        return Response(PayrollSerializer(payroll).data)

    @action(detail=True, methods=["get"])
    def payslip(self, request, pk=None):
        """Детальный расчётный лист."""
        payroll = self.get_object()
        return Response(PayslipSerializer(payroll).data)
