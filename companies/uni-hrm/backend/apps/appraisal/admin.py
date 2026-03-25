from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.appraisal.models import (
    AppraisalCycle,
    AppraisalScore,
    EmployeeAppraisal,
    KPIIndicator,
    TrainingProgram,
    TrainingRecord,
)


@admin.register(AppraisalCycle)
class AppraisalCycleAdmin(ModelAdmin):
    list_display = ["name", "start_date", "end_date", "status"]
    list_filter = ["status"]


@admin.register(KPIIndicator)
class KPIIndicatorAdmin(ModelAdmin):
    list_display = ["name", "category", "weight", "max_score"]
    list_filter = ["category"]


@admin.register(EmployeeAppraisal)
class EmployeeAppraisalAdmin(ModelAdmin):
    list_display = ["employee", "cycle", "status", "overall_score", "reviewed_at"]
    list_filter = ["status", "cycle"]


@admin.register(AppraisalScore)
class AppraisalScoreAdmin(ModelAdmin):
    list_display = ["appraisal", "kpi", "self_score", "manager_score", "final_score"]


@admin.register(TrainingProgram)
class TrainingProgramAdmin(ModelAdmin):
    list_display = ["name", "training_type", "provider", "duration_hours", "is_active"]
    list_filter = ["training_type", "is_active"]


@admin.register(TrainingRecord)
class TrainingRecordAdmin(ModelAdmin):
    list_display = ["employee", "program", "status", "start_date", "end_date"]
    list_filter = ["status"]
