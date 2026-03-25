from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.academic.models import (
    AcademicDegree,
    AcademicLoad,
    AcademicTitle,
    EmployeeAcademic,
    PositionContest,
    Subject,
)


@admin.register(AcademicDegree)
class AcademicDegreeAdmin(ModelAdmin):
    list_display = ["code", "country"]
    search_fields = ["code"]


@admin.register(AcademicTitle)
class AcademicTitleAdmin(ModelAdmin):
    list_display = ["code"]
    search_fields = ["code"]


@admin.register(EmployeeAcademic)
class EmployeeAcademicAdmin(ModelAdmin):
    list_display = ["employee", "degree", "title", "specialization", "awarded_date"]
    list_filter = ["degree", "title"]
    search_fields = ["employee__last_name", "employee__first_name"]
    raw_id_fields = ["employee"]


@admin.register(Subject)
class SubjectAdmin(ModelAdmin):
    list_display = ["code", "department", "credits", "is_active"]
    list_filter = ["is_active", "department"]
    search_fields = ["code"]


@admin.register(AcademicLoad)
class AcademicLoadAdmin(ModelAdmin):
    list_display = [
        "employee",
        "subject",
        "academic_year",
        "semester",
        "lecture_hours",
        "seminar_hours",
        "lab_hours",
        "load_type",
    ]
    list_filter = ["academic_year", "semester", "load_type"]
    search_fields = ["employee__last_name", "employee__first_name"]
    raw_id_fields = ["employee"]


@admin.register(PositionContest)
class PositionContestAdmin(ModelAdmin):
    list_display = [
        "department",
        "position",
        "application_deadline",
        "status",
        "winner",
    ]
    list_filter = ["status"]
    search_fields = ["department__code", "position__code"]
    raw_id_fields = ["winner"]
