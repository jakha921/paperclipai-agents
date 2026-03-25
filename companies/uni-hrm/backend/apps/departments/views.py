from django.db.models import Count, QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .filters import EmployeeFilter
from .models import Department, Employee, Position
from .serializers import (
    DepartmentListSerializer,
    DepartmentSerializer,
    EmployeeCreateSerializer,
    EmployeeDetailSerializer,
    EmployeeListSerializer,
    PositionSerializer,
)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet для подразделений."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["department_type", "is_active", "parent"]

    def get_queryset(self) -> QuerySet:
        return Department.objects.annotate(employee_count=Count("employees")).select_related("head")

    def get_serializer_class(self):
        if self.action == "list":
            return DepartmentListSerializer
        return DepartmentSerializer

    @action(detail=False, methods=["get"])
    def tree(self, request: Request) -> Response:
        """Дерево подразделений."""
        roots = (
            Department.objects.root_nodes()
            .filter(is_active=True)
            .annotate(employee_count=Count("employees"))
        )
        serializer = DepartmentSerializer(roots, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def children(self, request: Request, pk=None) -> Response:
        """Прямые дочерние подразделения."""
        department = self.get_object()
        children = (
            department.get_children()
            .filter(is_active=True)
            .annotate(employee_count=Count("employees"))
        )
        serializer = DepartmentListSerializer(children, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def org_chart(self, request: Request) -> Response:
        """Данные для org chart."""
        nodes = (
            Department.objects.filter(is_active=True)
            .select_related("head")
            .annotate(employee_count=Count("employees"))
        )
        result = []
        for dept in nodes:
            result.append(
                {
                    "id": str(dept.id),
                    "name": dept.get_name(),
                    "code": dept.code,
                    "type": dept.department_type,
                    "parentId": (str(dept.parent_id) if dept.parent_id else None),
                    "employee_count": dept.employee_count,
                    "head_name": (dept.head.full_name if dept.head else None),
                }
            )
        return Response(result)


class PositionViewSet(viewsets.ModelViewSet):
    """ViewSet для должностей."""

    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["category", "is_academic"]

    def get_queryset(self) -> QuerySet:
        return Position.objects.all()


class EmployeeViewSet(viewsets.ModelViewSet):
    """ViewSet для сотрудников."""

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeFilter

    def get_queryset(self) -> QuerySet:
        return (
            Employee.objects.filter(is_deleted=False)
            .select_related("department", "position", "user")
            .prefetch_related("history")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer
        if self.action in ("create", "update", "partial_update"):
            return EmployeeCreateSerializer
        return EmployeeDetailSerializer

    def perform_destroy(self, instance: Employee) -> None:
        instance.soft_delete()
