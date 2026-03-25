from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.leaves.models import LeaveAllocation, LeaveRequest, LeaveType, PublicHoliday


@admin.register(PublicHoliday)
class PublicHolidayAdmin(ModelAdmin):
    list_display = ["date", "is_working_day"]


@admin.register(LeaveType)
class LeaveTypeAdmin(ModelAdmin):
    list_display = ["code", "days_per_year", "is_paid", "requires_document"]


@admin.register(LeaveAllocation)
class LeaveAllocationAdmin(ModelAdmin):
    list_display = ["employee", "leave_type", "year", "total_days", "used_days"]
    list_filter = ["year", "leave_type"]


@admin.register(LeaveRequest)
class LeaveRequestAdmin(ModelAdmin):
    list_display = ["employee", "leave_type", "start_date", "end_date", "status"]
    list_filter = ["status", "leave_type"]
