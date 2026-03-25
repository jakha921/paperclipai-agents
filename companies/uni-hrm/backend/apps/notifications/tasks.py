from __future__ import annotations

import logging

try:
    from celery import shared_task
except ImportError:

    def shared_task(func):
        return func


logger = logging.getLogger(__name__)


def _send_telegram_message(chat_id: str, text: str) -> bool:
    """Отправить сообщение через Telegram Bot API."""
    import json
    import urllib.request

    from django.conf import settings

    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not configured")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "HTML"}).encode()

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception:
        logger.exception("Failed to send Telegram message to %s", chat_id)
        return False


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
        user = notification.recipient
        telegram_id = getattr(user, "telegram_id", None) or ""
        if telegram_id:
            _send_telegram_message(telegram_id, notification.message)
        else:
            logger.info("User %s has no telegram_id, skipping Telegram delivery", user.email)

    return {"status": "delivered", "id": str(notification.id), "channel": notification.channel}
