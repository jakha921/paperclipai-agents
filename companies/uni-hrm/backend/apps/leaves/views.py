from __future__ import annotations

from datetime import date

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.pagination import StandardPagination
from apps.leaves.filters import LeaveRequestFilter
from apps.leaves.models import LeaveAllocation, LeaveRequest, LeaveType, PublicHoliday
from apps.leaves.serializers import (
    LeaveAllocationSerializer,
    LeaveBalanceSerializer,
    LeaveCalendarEventSerializer,
    LeaveRequestSerializer,
    LeaveTypeSerializer,
    PublicHolidaySerializer,
)


class PublicHolidayViewSet(viewsets.ModelViewSet):
    queryset = PublicHoliday.objects.all()
    serializer_class = PublicHolidaySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination


class LeaveTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsAuthenticated]


class LeaveAllocationViewSet(viewsets.ModelViewSet):
    queryset = LeaveAllocation.objects.select_related("employee", "leave_type").all()
    serializer_class = LeaveAllocationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee", "year", "leave_type"]

    @action(detail=False, methods=["post"], url_path="allocate_year")
    def allocate_year(self, request: Request) -> Response:
        """Create/update allocations for all active employees for a given year (HR only)."""
        from apps.departments.models import Employee

        year = request.data.get("year", date.today().year)
        employees = Employee.objects.filter(status=Employee.Status.ACTIVE).select_related(
            "position"
        )
        created = 0
        for employee in employees:
            for leave_type in LeaveType.objects.all():
                category = employee.position.category if employee.position else None
                if not leave_type.applicable_categories:
                    applicable = True
                else:
                    applicable = category in leave_type.applicable_categories
                if applicable:
                    _, is_created = LeaveAllocation.objects.get_or_create(
                        employee=employee,
                        leave_type=leave_type,
                        year=year,
                        defaults={"total_days": leave_type.days_per_year},
                    )
                    if is_created:
                        created += 1
        return Response({"created": created, "year": year})


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related("employee", "leave_type", "approved_by").all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = LeaveRequestFilter

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if hasattr(user, "employee") and not (user.is_staff or user.is_superuser):
            qs = qs.filter(employee=user.employee)
        return qs

    @action(detail=True, methods=["post"])
    def submit(self, request: Request, pk=None) -> Response:
        """DRAFT -> PENDING_HEAD."""
        instance = self.get_object()
        if instance.status != LeaveRequest.Status.DRAFT:
            return Response(
                {"detail": "Только черновик можно отправить."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = LeaveRequest.Status.PENDING_HEAD
        instance.save(update_fields=["status", "updated_at"])
        return Response(LeaveRequestSerializer(instance).data)

    @action(detail=True, methods=["post"])
    def approve(self, request: Request, pk=None) -> Response:
        """PENDING_HEAD -> PENDING_HR (head) or PENDING_HR -> APPROVED (HR)."""
        instance = self.get_object()
        if instance.status == LeaveRequest.Status.PENDING_HEAD:
            instance.status = LeaveRequest.Status.PENDING_HR
        elif instance.status == LeaveRequest.Status.PENDING_HR:
            instance.status = LeaveRequest.Status.APPROVED
            instance.approved_by = request.user
        else:
            return Response(
                {"detail": "Невозможно одобрить в текущем статусе."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.save(update_fields=["status", "approved_by", "updated_at"])
        return Response(LeaveRequestSerializer(instance).data)

    @action(detail=True, methods=["post"])
    def reject(self, request: Request, pk=None) -> Response:
        """-> REJECTED."""
        instance = self.get_object()
        if instance.status not in [
            LeaveRequest.Status.PENDING_HEAD,
            LeaveRequest.Status.PENDING_HR,
        ]:
            return Response(
                {"detail": "Невозможно отклонить в текущем статусе."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = LeaveRequest.Status.REJECTED
        instance.rejection_reason = request.data.get("rejection_reason", "")
        instance.save(update_fields=["status", "rejection_reason", "updated_at"])
        return Response(LeaveRequestSerializer(instance).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request: Request, pk=None) -> Response:
        """-> CANCELLED (only DRAFT or PENDING_HEAD)."""
        instance = self.get_object()
        if instance.status not in [
            LeaveRequest.Status.DRAFT,
            LeaveRequest.Status.PENDING_HEAD,
        ]:
            return Response(
                {"detail": "Отменить можно только черновик или ожидающую заявку."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = LeaveRequest.Status.CANCELLED
        instance.save(update_fields=["status", "updated_at"])
        return Response(LeaveRequestSerializer(instance).data)

    @action(detail=False, methods=["get"])
    def balance(self, request: Request) -> Response:
        """Leave balance for current employee."""
        user = request.user
        if not hasattr(user, "employee"):
            return Response(
                {"detail": "Сотрудник не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )
        year = request.query_params.get("year", date.today().year)
        allocations = LeaveAllocation.objects.filter(
            employee=user.employee, year=year
        ).select_related("leave_type")
        data = [
            {
                "leave_type": alloc.leave_type,
                "total_days": alloc.total_days,
                "used_days": alloc.used_days,
                "carry_over_days": alloc.carry_over_days,
                "remaining_days": alloc.remaining_days,
            }
            for alloc in allocations
        ]
        return Response(LeaveBalanceSerializer(data, many=True).data)

    @action(detail=False, methods=["get"])
    def calendar(self, request: Request) -> Response:
        """Calendar events for department and month."""
        department_id = request.query_params.get("department")
        month = request.query_params.get("month")
        year = request.query_params.get("year", date.today().year)

        qs = LeaveRequest.objects.filter(status=LeaveRequest.Status.APPROVED).select_related(
            "employee", "employee__user", "leave_type"
        )

        if department_id:
            qs = qs.filter(employee__department_id=department_id)
        if month:
            qs = qs.filter(start_date__month=month, start_date__year=year)

        data = []
        for req in qs:
            employee_name = str(req.employee)
            data.append(
                {
                    "employee_name": employee_name,
                    "leave_type": req.leave_type.code,
                    "start_date": req.start_date,
                    "end_date": req.end_date,
                    "status": req.status,
                }
            )
        return Response(LeaveCalendarEventSerializer(data, many=True).data)
