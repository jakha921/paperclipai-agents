from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Заполнить БД всеми тестовыми данными"

    def handle(self, *args, **options):
        commands = [
            "seed_roles",
            "seed_settings",
            "seed_departments",
            "seed_users",
            "seed_leaves",
            "seed_attendance",
            "seed_payroll",
            "seed_academic",
            "seed_notifications",
            "seed_documents",
            "seed_demo",
        ]
        for cmd in commands:
            try:
                self.stdout.write(f"Running {cmd}...")
                call_command(cmd)
                self.stdout.write(self.style.SUCCESS(f"  {cmd} OK"))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  {cmd}: {e}"))
