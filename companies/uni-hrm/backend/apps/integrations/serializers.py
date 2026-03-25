from rest_framework import serializers

from .models import HEMISMapping, SyncConflict, SyncLog


class HEMISMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HEMISMapping
        fields = ["id", "content_type", "local_id", "hemis_id", "last_synced_at", "sync_status"]


class SyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncLog
        fields = [
            "id",
            "sync_type",
            "started_at",
            "completed_at",
            "status",
            "stats",
            "error_message",
        ]
        read_only_fields = fields


class SyncConflictSerializer(serializers.ModelSerializer):
    mapping = HEMISMappingSerializer(read_only=True)
    resolved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SyncConflict
        fields = [
            "id",
            "mapping",
            "field_name",
            "local_value",
            "hemis_value",
            "is_resolved",
            "resolution",
            "resolved_by",
            "resolved_by_name",
        ]
        read_only_fields = ["id", "mapping", "field_name", "local_value", "hemis_value"]

    def get_resolved_by_name(self, obj: SyncConflict) -> str | None:
        if obj.resolved_by:
            return str(obj.resolved_by)
        return None


class ResolveConflictSerializer(serializers.Serializer):
    resolution = serializers.ChoiceField(choices=["local", "hemis"])
