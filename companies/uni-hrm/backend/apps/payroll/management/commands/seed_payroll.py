from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.payroll.models import TaxConfiguration


class Command(BaseCommand):
    help = "Seed payroll data: TaxConfiguration for 2024, 2025"

    def handle(self, *args, **options):
        for year, min_wage in [(2024, Decimal("980638")), (2025, Decimal("1155000"))]:
            obj, created = TaxConfiguration.objects.update_or_create(
                year=year,
                defaults={
                    "ndfl_rate": Decimal("0.12"),
                    "social_tax_rate": Decimal("0.12"),
                    "inps_employee_rate": Decimal("0.001"),
                    "inps_employer_rate": Decimal("0.001"),
                    "minimum_wage": min_wage,
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{action} TaxConfiguration {year}"))
