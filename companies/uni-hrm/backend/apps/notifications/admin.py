from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.notifications.models import Notification, NotificationTemplate


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(ModelAdmin):
    list_display = ["code", "name", "channels", "created_at"]
    search_fields = ["code", "name"]


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ["recipient", "title", "channel", "is_read", "created_at"]
    list_filter = ["channel", "is_read"]
    search_fields = ["title", "message"]
    raw_id_fields = ["recipient", "template"]
