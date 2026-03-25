from django.contrib import admin

from .models import HEMISMapping, SyncConflict, SyncLog


@admin.register(HEMISMapping)
class HEMISMappingAdmin(admin.ModelAdmin):
    list_display = ["content_type", "local_id", "hemis_id", "sync_status", "last_synced_at"]
    list_filter = ["content_type", "sync_status"]


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ["sync_type", "status", "started_at", "completed_at"]
    list_filter = ["sync_type", "status"]
    readonly_fields = ["started_at", "completed_at", "stats", "error_message"]


@admin.register(SyncConflict)
class SyncConflictAdmin(admin.ModelAdmin):
    list_display = ["mapping", "field_name", "is_resolved", "resolution"]
    list_filter = ["is_resolved"]
