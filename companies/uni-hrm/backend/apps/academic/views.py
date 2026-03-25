from __future__ import annotations

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.academic.filters import (
    AcademicLoadFilter,
    EmployeeAcademicFilter,
    PositionContestFilter,
    SubjectFilter,
)
from apps.academic.models import (
    AcademicDegree,
    AcademicLoad,
    AcademicTitle,
    EmployeeAcademic,
    PositionContest,
    Subject,
)
from apps.academic.serializers import (
    AcademicDegreeSerializer,
    AcademicLoadSerializer,
    AcademicLoadSummarySerializer,
    AcademicTitleSerializer,
    EmployeeAcademicSerializer,
    PositionContestSerializer,
    SubjectSerializer,
)
from apps.academic.services import calculate_total_load


class AcademicDegreeViewSet(viewsets.ModelViewSet):
    """CRUD для академических степеней."""

    queryset = AcademicDegree.objects.all()
    serializer_class = AcademicDegreeSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["code"]


class AcademicTitleViewSet(viewsets.ModelViewSet):
    """CRUD для академических званий."""

    queryset = AcademicTitle.objects.all()
    serializer_class = AcademicTitleSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["code"]


class EmployeeAcademicViewSet(viewsets.ModelViewSet):
    """CRUD для академических данных сотрудников."""

    queryset = EmployeeAcademic.objects.select_related("employee", "degree", "title").all()
    serializer_class = EmployeeAcademicSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = EmployeeAcademicFilter

    def get_queryset(self):
        qs = super().get_queryset()
        employee_id = self.request.query_params.get("employee")
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        return qs


class SubjectViewSet(viewsets.ModelViewSet):
    """CRUD для учебных дисциплин."""

    queryset = Subject.objects.select_related("department").all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = SubjectFilter
    search_fields = ["code"]


class AcademicLoadViewSet(viewsets.ModelViewSet):
    """CRUD для учебной нагрузки."""

    queryset = AcademicLoad.objects.select_related("employee", "subject").all()
    serializer_class = AcademicLoadSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = AcademicLoadFilter

    @action(detail=False, methods=["get"])
    def summary(self, request: Request) -> Response:
        """Сводка нагрузки преподавателя за учебный год."""
        employee_id = request.query_params.get("employee")
        academic_year = request.query_params.get("academic_year")

        if not employee_id or not academic_year:
            return Response(
                {"detail": "Параметры employee и academic_year обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = calculate_total_load(employee_id, academic_year)
        serializer = AcademicLoadSummarySerializer(data)
        return Response(serializer.data)


class PositionContestViewSet(viewsets.ModelViewSet):
    """CRUD для конкурсов на замещение должностей."""

    queryset = PositionContest.objects.select_related("department", "position", "winner").all()
    serializer_class = PositionContestSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PositionContestFilter

    @action(detail=True, methods=["post"])
    def close(self, request: Request, pk=None) -> Response:
        """Закрыть конкурс."""
        contest = self.get_object()
        if contest.status != PositionContest.Status.OPEN:
            return Response(
                {"detail": "Можно закрыть только открытый конкурс."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        contest.status = PositionContest.Status.CLOSED
        contest.save(update_fields=["status", "updated_at"])
        return Response(PositionContestSerializer(contest).data)

    @action(detail=True, methods=["post"])
    def set_winner(self, request: Request, pk=None) -> Response:
        """Назначить победителя конкурса."""
        contest = self.get_object()
        winner_id = request.data.get("winner_id")

        if not winner_id:
            return Response(
                {"detail": "Параметр winner_id обязателен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if contest.status != PositionContest.Status.OPEN:
            return Response(
                {"detail": "Можно назначить победителя только в открытом конкурсе."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from apps.departments.models import Employee

        try:
            winner = Employee.objects.get(pk=winner_id)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Сотрудник не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        contest.winner = winner
        contest.status = PositionContest.Status.CLOSED
        contest.save(update_fields=["status", "winner", "updated_at"])
        return Response(PositionContestSerializer(contest).data)
