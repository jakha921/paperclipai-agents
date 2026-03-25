from __future__ import annotations

from rest_framework import serializers

from apps.notifications.models import Notification, NotificationTemplate


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = ["id", "code", "name", "title", "body", "channels", "created_at"]
        read_only_fields = ["created_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "recipient",
            "template",
            "title",
            "message",
            "channel",
            "is_read",
            "read_at",
            "data",
            "created_at",
        ]
        read_only_fields = [
            "recipient",
            "template",
            "title",
            "message",
            "channel",
            "is_read",
            "read_at",
            "data",
            "created_at",
        ]
