
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.payroll.models import TaxConfiguration


class TestTaxConfigurationAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.client.force_authenticate(user=self.user)

    def test_tax_config_list(self):
        TaxConfiguration.objects.create(year=2025)
        response = self.client.get("/api/v1/payroll/tax-configs/")
        assert response.status_code == 200

    def test_tax_config_create(self):
        response = self.client.post(
            "/api/v1/payroll/tax-configs/",
            {
                "year": 2026,
                "ndfl_rate": "0.12",
                "social_tax_rate": "0.12",
                "inps_employee_rate": "0.001",
                "inps_employer_rate": "0.001",
                "minimum_wage": "1200000",
            },
        )
        assert response.status_code == 201
        assert response.data["year"] == 2026

    def test_unauthenticated_access_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/payroll/tax-configs/")
        assert response.status_code == 401
