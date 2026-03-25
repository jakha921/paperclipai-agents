from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(ModelAdmin):
    list_display = ["site_name", "currency", "timezone", "updated_at"]
    fieldsets = [
        ("General", {"fields": ["site_name", "site_url", "currency", "timezone"]}),
        (
            "Working Hours",
            {"fields": ["working_hours_start", "working_hours_end", "working_days"]},
        ),
        ("Leave Policies", {"fields": ["annual_leave_days", "sick_leave_days"]}),
        (
            "Email",
            {"fields": ["smtp_host", "smtp_port", "smtp_use_tls", "smtp_username", "from_email"]},
        ),
    ]
