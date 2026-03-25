from django.contrib import admin

from apps.payroll.models import EmployeeSalary, Payroll, TaxConfiguration


@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(admin.ModelAdmin):
    list_display = ["year", "ndfl_rate", "social_tax_rate", "minimum_wage"]
    ordering = ["-year"]


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ["employee", "base_salary", "effective_from", "is_active"]
    list_filter = ["is_active"]


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ["employee", "month", "year", "gross_salary", "net_salary", "status"]
    list_filter = ["status", "year", "month"]
    readonly_fields = ["gross_salary", "net_salary", "total_deductions"]
