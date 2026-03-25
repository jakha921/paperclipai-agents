from django.core.management.base import BaseCommand

from apps.notifications.models import NotificationTemplate

TEMPLATES = [
    {
        "code": "leave_request_created",
        "name": "Заявка на отпуск создана",
        "title": {
            "ru": "Заявка на отпуск отправлена",
            "uz": "Ta'til so'rovi yuborildi",
            "en": "Leave request submitted",
        },
        "body": {
            "ru": "Ваша заявка на отпуск ({start_date} — {end_date}) отправлена на рассмотрение.",
            "uz": "Sizning ta'til so'rovingiz ({start_date} — {end_date}) ko'rib chiqishga yuborildi.",
            "en": "Your leave request ({start_date} — {end_date}) has been submitted for review.",
        },
        "channels": ["in_app"],
    },
    {
        "code": "leave_approved",
        "name": "Отпуск одобрен",
        "title": {
            "ru": "Отпуск одобрен",
            "uz": "Ta'til tasdiqlandi",
            "en": "Leave approved",
        },
        "body": {
            "ru": "Ваша заявка на отпуск ({start_date} — {end_date}) одобрена.",
            "uz": "Sizning ta'til so'rovingiz ({start_date} — {end_date}) tasdiqlandi.",
            "en": "Your leave request ({start_date} — {end_date}) has been approved.",
        },
        "channels": ["in_app", "email"],
    },
    {
        "code": "leave_rejected",
        "name": "Отпуск отклонён",
        "title": {
            "ru": "Отпуск отклонён",
            "uz": "Ta'til rad etildi",
            "en": "Leave rejected",
        },
        "body": {
            "ru": "Ваша заявка на отпуск ({start_date} — {end_date}) отклонена.",
            "uz": "Sizning ta'til so'rovingiz ({start_date} — {end_date}) rad etildi.",
            "en": "Your leave request ({start_date} — {end_date}) has been rejected.",
        },
        "channels": ["in_app", "email"],
    },
    {
        "code": "payslip_ready",
        "name": "Расчётный листок готов",
        "title": {
            "ru": "Расчётный листок готов",
            "uz": "Ish haqi varaqasi tayyor",
            "en": "Payslip ready",
        },
        "body": {
            "ru": "Ваш расчётный листок за {period} доступен для просмотра.",
            "uz": "Sizning {period} uchun ish haqi varaqangiz ko'rish uchun tayyor.",
            "en": "Your payslip for {period} is ready for viewing.",
        },
        "channels": ["in_app"],
    },
]


class Command(BaseCommand):
    help = "Seed notification templates"

    def handle(self, *args, **options):
        created_count = 0
        for tpl_data in TEMPLATES:
            _, created = NotificationTemplate.objects.update_or_create(
                code=tpl_data["code"],
                defaults={
                    "name": tpl_data["name"],
                    "title": tpl_data["title"],
                    "body": tpl_data["body"],
                    "channels": tpl_data["channels"],
                },
            )
            if created:
                created_count += 1
            self.stdout.write(f"  {'Created' if created else 'Updated'}: {tpl_data['code']}")

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created: {created_count}, Total: {len(TEMPLATES)}")
        )
