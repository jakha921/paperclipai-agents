from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.attendance.models import AttendanceRecord, EmployeeSchedule, TimeSheet, WorkSchedule


@admin.register(WorkSchedule)
class WorkScheduleAdmin(ModelAdmin):
    list_display = ["name", "schedule_type", "work_start", "work_end"]


@admin.register(EmployeeSchedule)
class EmployeeScheduleAdmin(ModelAdmin):
    list_display = ["employee", "schedule", "effective_from", "effective_to"]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(ModelAdmin):
    list_display = ["employee", "date", "status", "worked_hours", "source"]
    list_filter = ["status", "source"]


@admin.register(TimeSheet)
class TimeSheetAdmin(ModelAdmin):
    list_display = ["employee", "month", "year", "status", "total_hours"]
    list_filter = ["status", "year", "month"]
