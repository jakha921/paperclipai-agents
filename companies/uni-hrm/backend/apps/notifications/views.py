from __future__ import annotations

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.pagination import StandardPagination
from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.notifications.services import mark_all_read


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для уведомлений текущего пользователя."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related("template")

    @action(detail=False, methods=["get"])
    def unread_count(self, request: Request) -> Response:
        """Количество непрочитанных уведомлений."""
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({"count": count})

    @action(detail=True, methods=["post"])
    def mark_read(self, request: Request, pk=None) -> Response:
        """Пометить одно уведомление как прочитанное."""
        notification = self.get_object()
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at", "updated_at"])
        return Response(NotificationSerializer(notification).data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request: Request) -> Response:
        """Пометить все уведомления как прочитанные."""
        count = mark_all_read(request.user)
        return Response({"marked": count}, status=status.HTTP_200_OK)
