from django.core.management.base import BaseCommand

from apps.academic.models import AcademicDegree, AcademicTitle


class Command(BaseCommand):
    help = "Seed academic degrees and titles"

    def handle(self, *args, **options):
        degrees = [
            {
                "code": "phd",
                "name": {"ru": "PhD", "uz": "PhD", "en": "PhD"},
                "country": "",
            },
            {
                "code": "dsc",
                "name": {"ru": "DSc", "uz": "DSc", "en": "DSc"},
                "country": "",
            },
            {
                "code": "candidate",
                "name": {
                    "ru": "Кандидат наук",
                    "uz": "Fan nomzodi",
                    "en": "Candidate of Sciences",
                },
                "country": "",
            },
            {
                "code": "doctor",
                "name": {
                    "ru": "Доктор наук",
                    "uz": "Fan doktori",
                    "en": "Doctor of Sciences",
                },
                "country": "",
            },
        ]
        for d in degrees:
            AcademicDegree.objects.get_or_create(code=d["code"], defaults=d)

        titles = [
            {
                "code": "docent",
                "name": {
                    "ru": "Доцент",
                    "uz": "Dotsent",
                    "en": "Associate Professor",
                },
            },
            {
                "code": "professor",
                "name": {
                    "ru": "Профессор",
                    "uz": "Professor",
                    "en": "Professor",
                },
            },
            {
                "code": "senior_researcher",
                "name": {
                    "ru": "Старший научный сотрудник",
                    "uz": "Katta ilmiy xodim",
                    "en": "Senior Researcher",
                },
            },
        ]
        for t in titles:
            AcademicTitle.objects.get_or_create(code=t["code"], defaults=t)

        self.stdout.write(self.style.SUCCESS("Academic data seeded successfully"))
