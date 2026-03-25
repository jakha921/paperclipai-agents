from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.payroll.views import EmployeeSalaryViewSet, PayrollViewSet, TaxConfigurationViewSet

router = DefaultRouter()
router.register("tax-configs", TaxConfigurationViewSet, basename="tax-config")
router.register("salaries", EmployeeSalaryViewSet, basename="employee-salary")
router.register("payrolls", PayrollViewSet, basename="payroll")

urlpatterns = [
    path("", include(router.urls)),
]
