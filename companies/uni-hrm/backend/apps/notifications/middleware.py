from __future__ import annotations

import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)
User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_str: str):
    """Получить пользователя из JWT access token."""
    try:
        access_token = AccessToken(token_str)
        user_id = access_token["user_id"]
        return User.objects.get(id=user_id)
    except Exception:
        logger.warning("WS JWT auth failed for token: %s...", token_str[:10])
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """Middleware для JWT аутентификации WebSocket соединений.

    Читает token из query string: ws://host/ws/notifications/?token=JWT_TOKEN
    """

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token", [])

        if token_list:
            scope["user"] = await get_user_from_token(token_list[0])
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
