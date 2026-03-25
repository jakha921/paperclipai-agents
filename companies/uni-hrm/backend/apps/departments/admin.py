from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from unfold.admin import ModelAdmin, TabularInline

from .models import Department, Employee, EmploymentHistory, Position


class EmploymentHistoryInline(TabularInline):
    model = EmploymentHistory
    extra = 0
    readonly_fields = ["created_at"]


@admin.register(Department)
class DepartmentAdmin(DraggableMPTTAdmin, ModelAdmin):
    list_display = [
        "tree_actions",
        "indented_title",
        "code",
        "department_type",
        "is_active",
    ]
    list_display_links = ["indented_title"]
    search_fields = ["code", "name"]
    list_filter = ["department_type", "is_active"]


@admin.register(Position)
class PositionAdmin(ModelAdmin):
    list_display = [
        "__str__",
        "code",
        "category",
        "is_academic",
        "min_salary",
        "max_salary",
    ]
    search_fields = ["code", "name"]
    list_filter = ["category", "is_academic"]


@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    list_display = [
        "employee_number",
        "full_name",
        "department",
        "position",
        "status",
        "hire_date",
    ]
    search_fields = [
        "first_name",
        "last_name",
        "middle_name",
        "employee_number",
        "pinfl",
    ]
    list_filter = ["status", "contract_type", "department", "position"]
    inlines = [EmploymentHistoryInline]
    readonly_fields = ["employee_number", "created_at", "updated_at"]
