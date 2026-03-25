from rest_framework import serializers

from .models import SystemSettings


class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = [
            "id",
            "site_name",
            "site_url",
            "working_hours_start",
            "working_hours_end",
            "working_days",
            "annual_leave_days",
            "sick_leave_days",
            "currency",
            "timezone",
            "smtp_host",
            "smtp_port",
            "smtp_use_tls",
            "smtp_username",
            "from_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
