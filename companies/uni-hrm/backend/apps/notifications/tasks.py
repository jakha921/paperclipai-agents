from __future__ import annotations

try:
    from celery import shared_task
except ImportError:

    def shared_task(func):
        return func


@shared_task
def deliver_notification(notification_id: str) -> dict:
    """Доставить уведомление через внешний канал (email, telegram).

    Для in_app уведомлений доставка происходит через WebSocket в services.py.
    """
    from apps.notifications.models import Notification

    try:
        notification = Notification.objects.get(id=notification_id)
    except Notification.DoesNotExist:
        return {"status": "not_found", "id": notification_id}

    if notification.channel == Notification.Channel.EMAIL:
        # TODO: интеграция с email backend
        pass
    elif notification.channel == Notification.Channel.TELEGRAM:
        # TODO: интеграция с Telegram Bot API
        pass

    return {"status": "delivered", "id": str(notification.id), "channel": notification.channel}
