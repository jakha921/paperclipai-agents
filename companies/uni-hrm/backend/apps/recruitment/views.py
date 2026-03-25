from __future__ import annotations

from datetime import date

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .filters import CandidateFilter, InterviewFilter, VacancyFilter
from .models import Candidate, Interview, Vacancy
from .serializers import (
    CandidateCreateSerializer,
    CandidateDetailSerializer,
    CandidateListSerializer,
    InterviewSerializer,
    VacancyCreateSerializer,
    VacancyDetailSerializer,
    VacancyListSerializer,
)


class VacancyViewSet(viewsets.ModelViewSet):
    """CRUD для вакансий."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = VacancyFilter
    search_fields = ["requirements", "responsibilities"]
    ordering_fields = ["created_at", "deadline", "status"]

    def get_queryset(self):
        return (
            Vacancy.objects.select_related("department", "position")
            .annotate_candidates_count()
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return VacancyListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return VacancyCreateSerializer
        return VacancyDetailSerializer

    @action(detail=True, methods=["post"])
    def publish(self, request: Request, pk: str | None = None) -> Response:
        """Открыть вакансию (DRAFT → OPEN)."""
        vacancy = self.get_object()
        vacancy.status = Vacancy.Status.OPEN
        vacancy.save(update_fields=["status", "updated_at"])
        return Response({"status": vacancy.status})

    @action(detail=True, methods=["post"])
    def close(self, request: Request, pk: str | None = None) -> Response:
        """Закрыть вакансию."""
        vacancy = self.get_object()
        vacancy.status = Vacancy.Status.CLOSED
        vacancy.save(update_fields=["status", "updated_at"])
        return Response({"status": vacancy.status})


class CandidateViewSet(viewsets.ModelViewSet):
    """CRUD для кандидатов."""

    queryset = Candidate.objects.select_related("vacancy")
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CandidateFilter
    search_fields = ["first_name", "last_name", "phone", "email"]
    ordering_fields = ["applied_at", "stage"]

    def get_serializer_class(self):
        if self.action == "list":
            return CandidateListSerializer
        if self.action in ["create", "update", "partial_update"]:
            return CandidateCreateSerializer
        return CandidateDetailSerializer

    @action(detail=True, methods=["post"])
    def hire(self, request: Request, pk: str | None = None) -> Response:
        """Нанять кандидата: создать Employee, установить stage=HIRED."""
        from apps.departments.models import Employee

        candidate = self.get_object()

        required = ["pinfl", "passport_series", "birth_date", "gender", "nationality"]
        missing = [f for f in required if not request.data.get(f)]
        if missing:
            return Response(
                {"detail": f"Обязательные поля: {', '.join(missing)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not candidate.vacancy.position_id and not request.data.get("position"):
            return Response(
                {"detail": "Должность обязательна: укажите position в запросе или в вакансии"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        hire_date_raw = request.data.get("hire_date", date.today().isoformat())
        position_id = candidate.vacancy.position_id or request.data.get("position")

        with transaction.atomic():
            employee = Employee.objects.create(
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                middle_name=candidate.middle_name,
                phone=candidate.phone,
                email=candidate.email,
                department=candidate.vacancy.department,
                position_id=position_id,
                hire_date=hire_date_raw,
                contract_type=request.data.get("contract_type", Employee.ContractType.PERMANENT),
                pinfl=request.data["pinfl"],
                passport_series=request.data["passport_series"],
                birth_date=request.data["birth_date"],
                gender=request.data["gender"],
                nationality=request.data["nationality"],
            )
            candidate.stage = Candidate.Stage.HIRED
            candidate.save(update_fields=["stage", "updated_at"])

        return Response({"employee_id": str(employee.id)}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def reject(self, request: Request, pk: str | None = None) -> Response:
        """Отклонить кандидата."""
        candidate = self.get_object()
        candidate.stage = Candidate.Stage.REJECTED
        candidate.save(update_fields=["stage", "updated_at"])
        return Response({"stage": candidate.stage})


class InterviewViewSet(viewsets.ModelViewSet):
    """CRUD для интервью."""

    queryset = Interview.objects.select_related("candidate", "interviewer")
    permission_classes = [IsAuthenticated]
    serializer_class = InterviewSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = InterviewFilter
    ordering_fields = ["scheduled_at"]
