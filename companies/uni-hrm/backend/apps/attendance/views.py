from __future__ import annotations

import csv
import datetime
import io

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.attendance.filters import AttendanceRecordFilter, TimeSheetFilter
from apps.attendance.models import AttendanceRecord, EmployeeSchedule, TimeSheet, WorkSchedule
from apps.attendance.serializers import (
    AttendanceRecordSerializer,
    BulkAttendanceSerializer,
    EmployeeScheduleSerializer,
    TimeSheetSerializer,
    WorkScheduleSerializer,
)
from apps.core.pagination import StandardPagination


class WorkScheduleViewSet(viewsets.ModelViewSet):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer
    permission_classes = [IsAuthenticated]


class EmployeeScheduleViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSchedule.objects.select_related("employee", "schedule").all()
    serializer_class = EmployeeScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["employee"]


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related("employee").all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = AttendanceRecordFilter

    @action(detail=False, methods=["post"], url_path="bulk_create")
    def bulk_create(self, request: Request) -> Response:
        """Bulk create attendance records for a department/day."""
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        records_data = serializer.validated_data["records"]
        created = []
        for record_data in records_data:
            record, _ = AttendanceRecord.objects.update_or_create(
                employee=record_data["employee"],
                date=record_data["date"],
                defaults={k: v for k, v in record_data.items() if k not in ["employee", "date"]},
            )
            created.append(record)
        return Response(
            AttendanceRecordSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="import_csv")
    def import_csv(self, request: Request) -> Response:
        """Import attendance records from CSV."""
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"detail": "CSV файл не предоставлен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.departments.models import Employee

        content = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        created_count = 0
        errors = []

        for i, row in enumerate(reader):
            try:
                employee = Employee.objects.get(id=row["employee_id"])
                record_date = datetime.date.fromisoformat(row["date"])
                AttendanceRecord.objects.update_or_create(
                    employee=employee,
                    date=record_date,
                    defaults={
                        "check_in": row.get("check_in") or None,
                        "check_out": row.get("check_out") or None,
                        "status": row.get("status", AttendanceRecord.Status.PRESENT),
                        "source": AttendanceRecord.Source.IMPORT,
                    },
                )
                created_count += 1
            except Exception as e:
                errors.append({"row": i + 1, "error": str(e)})

        return Response({"created": created_count, "errors": errors})


class TimeSheetViewSet(viewsets.ModelViewSet):
    queryset = TimeSheet.objects.select_related("employee", "approved_by").all()
    serializer_class = TimeSheetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = TimeSheetFilter

    @action(detail=True, methods=["post"])
    def submit(self, request: Request, pk=None) -> Response:
        """DRAFT -> SUBMITTED."""
        instance = self.get_object()
        if instance.status != TimeSheet.Status.DRAFT:
            return Response(
                {"detail": "Только черновик можно отправить."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = TimeSheet.Status.SUBMITTED
        instance.save(update_fields=["status", "updated_at"])
        return Response(TimeSheetSerializer(instance).data)

    @action(detail=True, methods=["post"])
    def approve(self, request: Request, pk=None) -> Response:
        """SUBMITTED -> APPROVED."""
        instance = self.get_object()
        if instance.status != TimeSheet.Status.SUBMITTED:
            return Response(
                {"detail": "Только отправленный табель можно утвердить."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = TimeSheet.Status.APPROVED
        instance.approved_by = request.user
        instance.save(update_fields=["status", "approved_by", "updated_at"])
        return Response(TimeSheetSerializer(instance).data)
