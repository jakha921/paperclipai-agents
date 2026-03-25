import logging

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SyncConflict, SyncLog
from .serializers import (
    ResolveConflictSerializer,
    SyncConflictSerializer,
    SyncLogSerializer,
)

logger = logging.getLogger(__name__)


class HEMISSyncViewSet(viewsets.ViewSet):
    """ViewSet для управления синхронизацией с HEMIS."""

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["post"])
    def sync(self, request):
        """Запустить синхронизацию."""
        sync_type = request.data.get("sync_type", "full")

        try:
            from .tasks import run_full_sync, sync_departments_from_hemis, sync_employees_from_hemis

            if sync_type == "departments":
                try:
                    task = sync_departments_from_hemis.delay()
                    return Response({"task_id": task.id, "status": "queued"})
                except AttributeError:
                    result = sync_departments_from_hemis()
                    return Response({"status": "completed", "result": result})

            elif sync_type == "employees":
                try:
                    task = sync_employees_from_hemis.delay()
                    return Response({"task_id": task.id, "status": "queued"})
                except AttributeError:
                    result = sync_employees_from_hemis()
                    return Response({"status": "completed", "result": result})

            else:  # full
                try:
                    task = run_full_sync.delay()
                    return Response({"task_id": task.id, "status": "queued"})
                except AttributeError:
                    run_full_sync()
                    return Response({"status": "completed"})

        except Exception as exc:
            logger.error("Sync error: %s", exc)
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"])
    def status_info(self, request):
        """Статус последней синхронизации."""
        last_log = SyncLog.objects.order_by("-started_at").first()
        if not last_log:
            return Response({"status": "never_synced", "last_sync": None})
        return Response(SyncLogSerializer(last_log).data)

    @action(detail=False, methods=["get"])
    def conflicts(self, request):
        """Список конфликтов."""
        is_resolved = request.query_params.get("resolved")
        qs = SyncConflict.objects.select_related("mapping", "resolved_by").all()
        if is_resolved == "false":
            qs = qs.filter(is_resolved=False)
        elif is_resolved == "true":
            qs = qs.filter(is_resolved=True)
        return Response(SyncConflictSerializer(qs, many=True).data)

    @action(detail=True, methods=["post"], url_path="resolve")
    def resolve_conflict(self, request, pk=None):
        """Решить конфликт."""
        try:
            conflict = SyncConflict.objects.get(pk=pk)
        except SyncConflict.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = ResolveConflictSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conflict.is_resolved = True
        conflict.resolution = serializer.validated_data["resolution"]
        conflict.resolved_by = request.user
        conflict.save(update_fields=["is_resolved", "resolution", "resolved_by"])

        return Response(SyncConflictSerializer(conflict).data)


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра логов синхронизации."""

    queryset = SyncLog.objects.all()
    serializer_class = SyncLogSerializer
    permission_classes = [IsAuthenticated]
