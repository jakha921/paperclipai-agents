from django.core.management.base import BaseCommand

from apps.settings.models import SETTINGS_UUID, SystemSettings


class Command(BaseCommand):
    help = "Seed default system settings"

    def handle(self, *args, **kwargs):
        obj, created = SystemSettings.objects.get_or_create(pk=SETTINGS_UUID)
        if created:
            obj.working_days = [1, 2, 3, 4, 5]
            obj.save()
            self.stdout.write(self.style.SUCCESS("System settings created with defaults"))
        else:
            self.stdout.write(self.style.WARNING("System settings already exist"))
