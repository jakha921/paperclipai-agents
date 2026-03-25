from django.core.management.base import BaseCommand

from apps.documents.models import DocumentTemplate

TEMPLATES = [
    {
        "name": "Приказ о приёме на работу",
        "code": "hiring_order",
        "template_html": (
            "<!DOCTYPE html><html><head>"
            "<style>body{font-family:Arial;margin:40px;}</style></head>"
            "<body><h2 style='text-align:center'>ПРИКАЗ №{{ order_number }}</h2>"
            "<h3 style='text-align:center'>О приёме на работу</h3>"
            "<p>Принять <strong>{{ employee.full_name }}</strong> "
            "на должность с {{ date }}.</p>"
            "<p>Директор: _____________</p></body></html>"
        ),
        "output_format": "pdf",
    },
    {
        "name": "Приказ об увольнении",
        "code": "dismissal_order",
        "template_html": (
            "<!DOCTYPE html><html><head>"
            "<style>body{font-family:Arial;margin:40px;}</style></head>"
            "<body><h2 style='text-align:center'>ПРИКАЗ №{{ order_number }}</h2>"
            "<h3 style='text-align:center'>Об увольнении</h3>"
            "<p>Уволить <strong>{{ employee }}</strong> с {{ date }}.</p>"
            "<p>Директор: _____________</p></body></html>"
        ),
        "output_format": "pdf",
    },
    {
        "name": "Трудовой договор",
        "code": "contract",
        "template_html": (
            "<!DOCTYPE html><html><head>"
            "<style>body{font-family:Arial;margin:40px;}</style></head>"
            "<body><h2 style='text-align:center'>ТРУДОВОЙ ДОГОВОР</h2>"
            "<p>Настоящий договор заключён с {{ employee }} {{ date }}.</p>"
            "<p>Подписи сторон: _____________</p></body></html>"
        ),
        "output_format": "pdf",
    },
    {
        "name": "Справка с места работы",
        "code": "reference",
        "template_html": (
            "<!DOCTYPE html><html><head>"
            "<style>body{font-family:Arial;margin:40px;}</style></head>"
            "<body><h2 style='text-align:center'>СПРАВКА</h2>"
            "<p>Настоящая справка выдана {{ employee }} в том, "
            "что он(а) работает в университете. Дата: {{ date }}</p>"
            "<p>Директор: _____________</p></body></html>"
        ),
        "output_format": "pdf",
    },
    {
        "name": "Приказ об отпуске",
        "code": "leave_order",
        "template_html": (
            "<!DOCTYPE html><html><head>"
            "<style>body{font-family:Arial;margin:40px;}</style></head>"
            "<body><h2 style='text-align:center'>ПРИКАЗ №{{ order_number }}</h2>"
            "<h3 style='text-align:center'>О предоставлении отпуска</h3>"
            "<p>Предоставить {{ employee }} отпуск с {{ date }}.</p>"
            "<p>Директор: _____________</p></body></html>"
        ),
        "output_format": "pdf",
    },
]


class Command(BaseCommand):
    help = "Seed document templates"

    def handle(self, *args, **options):
        for tpl in TEMPLATES:
            obj, created = DocumentTemplate.objects.update_or_create(
                code=tpl["code"],
                defaults=tpl,
            )
            label = "Created" if created else "Updated"
            self.stdout.write(f"{label}: {obj.name}")
        self.stdout.write(self.style.SUCCESS("Done seeding document templates."))
