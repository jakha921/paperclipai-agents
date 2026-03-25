from django.http import FileResponse, HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import analytics, services
from .models import DocumentTemplate, GeneratedDocument
from .serializers import (
    DocumentTemplateSerializer,
    GeneratedDocumentSerializer,
    GenerateDocumentSerializer,
)


class DocumentTemplateViewSet(viewsets.ModelViewSet):
    queryset = DocumentTemplate.objects.filter(is_active=True)
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAuthenticated]


class GeneratedDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GeneratedDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GeneratedDocument.objects.select_related(
            "template", "employee", "generated_by"
        ).all()

    @action(detail=False, methods=["post"])
    def generate(self, request):
        serializer = GenerateDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            doc = services.generate_document(
                template_code=serializer.validated_data["template_code"],
                employee_id=serializer.validated_data["employee_id"],
                extra_data=serializer.validated_data.get("extra_data", {}),
                user=request.user,
            )
            return Response(
                GeneratedDocumentSerializer(doc, context={"request": request}).data,
                status=status.HTTP_201_CREATED,
            )
        except DocumentTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        doc = self.get_object()
        if not doc.file:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(
            doc.file.open(),
            as_attachment=True,
            filename=doc.file.name.split("/")[-1],
        )


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def payroll_excel(self, request):
        year = int(request.data.get("year", 0))
        month = int(request.data.get("month", 0))
        department_id = request.data.get("department_id")

        if not year or not month:
            return Response(
                {"error": "year and month are required"}, status=status.HTTP_400_BAD_REQUEST
            )

        excel_bytes = services.generate_payroll_excel(year, month, department_id)

        response = HttpResponse(
            excel_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="payroll_{year}_{month}.xlsx"'
        return response

    @action(detail=False, methods=["post"])
    def employees_excel(self, request):
        filters = {
            "department_id": request.data.get("department_id"),
            "status": request.data.get("status"),
        }

        excel_bytes = services.generate_employee_excel(filters)

        response = HttpResponse(
            excel_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="employees.xlsx"'
        return response


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        return Response(analytics.get_dashboard_stats())

    @action(detail=False, methods=["get"])
    def turnover(self, request):
        months = int(request.query_params.get("months", 12))
        return Response(analytics.get_turnover_stats(months))

    @action(detail=False, methods=["get"])
    def departments(self, request):
        return Response(analytics.get_department_stats())

    @action(detail=False, methods=["get"])
    def demographics(self, request):
        return Response(analytics.get_demographics())
