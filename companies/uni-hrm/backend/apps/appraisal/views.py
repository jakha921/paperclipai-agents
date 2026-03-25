from __future__ import annotations

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.appraisal.filters import EmployeeAppraisalFilter, TrainingRecordFilter
from apps.appraisal.models import (
    AppraisalCycle,
    AppraisalScore,
    EmployeeAppraisal,
    KPIIndicator,
    TrainingProgram,
    TrainingRecord,
)
from apps.appraisal.serializers import (
    AppraisalCycleSerializer,
    AppraisalScoreSerializer,
    EmployeeAppraisalSerializer,
    KPIIndicatorSerializer,
    TrainingProgramSerializer,
    TrainingRecordSerializer,
)
from apps.appraisal.services import calculate_weighted_score


class AppraisalCycleViewSet(viewsets.ModelViewSet):
    """CRUD для циклов аттестации."""

    queryset = AppraisalCycle.objects.prefetch_related("applicable_departments").all()
    serializer_class = AppraisalCycleSerializer
    permission_classes = [IsAuthenticated]


class KPIIndicatorViewSet(viewsets.ModelViewSet):
    """CRUD для показателей KPI."""

    queryset = KPIIndicator.objects.all()
    serializer_class = KPIIndicatorSerializer
    permission_classes = [IsAuthenticated]


class EmployeeAppraisalViewSet(viewsets.ModelViewSet):
    """CRUD + workflow actions для аттестации сотрудников."""

    queryset = (
        EmployeeAppraisal.objects.select_related("cycle", "employee", "reviewer")
        .prefetch_related("scores__kpi")
        .all()
    )
    serializer_class = EmployeeAppraisalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeAppraisalFilter

    @action(detail=True, methods=["post"], url_path="self-review")
    def self_review(self, request: Request, pk=None) -> Response:
        """Перевести аттестацию в статус самооценки."""
        instance = self.get_object()
        if instance.status != EmployeeAppraisal.Status.PENDING:
            return Response(
                {"detail": "Только ожидающую аттестацию можно перевести в самооценку."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = EmployeeAppraisal.Status.SELF_REVIEW
        instance.save(update_fields=["status", "updated_at"])
        return Response(EmployeeAppraisalSerializer(instance).data)

    @action(detail=True, methods=["post"], url_path="manager-review")
    def manager_review(self, request: Request, pk=None) -> Response:
        """Перевести в статус оценки руководителя и вычислить overall_score."""
        instance = self.get_object()
        if instance.status != EmployeeAppraisal.Status.SELF_REVIEW:
            return Response(
                {"detail": "Оценка руководителя доступна только после самооценки."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = EmployeeAppraisal.Status.MANAGER_REVIEW
        instance.overall_score = calculate_weighted_score(instance)
        instance.save(update_fields=["status", "overall_score", "updated_at"])
        return Response(EmployeeAppraisalSerializer(instance).data)

    @action(detail=True, methods=["post"])
    def complete(self, request: Request, pk=None) -> Response:
        """Завершить аттестацию."""
        instance = self.get_object()
        if instance.status != EmployeeAppraisal.Status.MANAGER_REVIEW:
            return Response(
                {"detail": "Завершить можно только после оценки руководителя."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.status = EmployeeAppraisal.Status.COMPLETED
        instance.overall_score = calculate_weighted_score(instance)
        instance.reviewed_at = timezone.now()
        instance.save(update_fields=["status", "overall_score", "reviewed_at", "updated_at"])
        return Response(EmployeeAppraisalSerializer(instance).data)


class AppraisalScoreViewSet(viewsets.ModelViewSet):
    """CRUD для оценок KPI."""

    queryset = AppraisalScore.objects.select_related("appraisal", "kpi").all()
    serializer_class = AppraisalScoreSerializer
    permission_classes = [IsAuthenticated]


class TrainingProgramViewSet(viewsets.ModelViewSet):
    """CRUD для программ обучения."""

    queryset = TrainingProgram.objects.all()
    serializer_class = TrainingProgramSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ("true", "1"))
        return qs


class TrainingRecordViewSet(viewsets.ModelViewSet):
    """CRUD для записей об обучении."""

    queryset = TrainingRecord.objects.select_related("employee", "program").all()
    serializer_class = TrainingRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TrainingRecordFilter
