from __future__ import annotations

from typing import TYPE_CHECKING

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from apps.notifications.models import Notification, NotificationTemplate

if TYPE_CHECKING:
    from apps.accounts.models import User


def send_notification(
    recipient: User,
    title: str,
    message: str,
    channel: str = Notification.Channel.IN_APP,
    data: dict | None = None,
    template: NotificationTemplate | None = None,
) -> Notification:
    """Создать уведомление и отправить через WebSocket."""
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        channel=channel,
        data=data or {},
        template=template,
    )

    if channel == Notification.Channel.IN_APP:
        _push_to_websocket(notification)

    return notification


def send_from_template(
    recipient: User,
    template_code: str,
    context: dict | None = None,
    language: str = "ru",
) -> list[Notification]:
    """Отправить уведомление по шаблону на все каналы шаблона."""
    try:
        template = NotificationTemplate.objects.get(code=template_code)
    except NotificationTemplate.DoesNotExist:
        return []

    ctx = context or {}
    title = template.title.get(language, template.title.get("ru", ""))
    body = template.body.get(language, template.body.get("ru", ""))

    # Подстановка переменных
    try:
        title = title.format(**ctx)
        body = body.format(**ctx)
    except (KeyError, IndexError):
        pass

    notifications = []
    for ch in template.channels:
        notification = send_notification(
            recipient=recipient,
            title=title,
            message=body,
            channel=ch,
            data=ctx,
            template=template,
        )
        notifications.append(notification)
    return notifications


def mark_all_read(user: User) -> int:
    """Пометить все уведомления пользователя как прочитанные."""
    now = timezone.now()
    count = Notification.objects.filter(recipient=user, is_read=False).update(
        is_read=True, read_at=now
    )
    return count


def _push_to_websocket(notification: Notification) -> None:
    """Отправить уведомление в WebSocket группу пользователя."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    group_name = f"user_{notification.recipient_id}"
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "notification.message",
            "data": {
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "channel": notification.channel,
                "is_read": notification.is_read,
                "data": notification.data,
                "created_at": notification.created_at.isoformat(),
            },
        },
    )
