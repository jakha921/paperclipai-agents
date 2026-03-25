from django.core.management.base import BaseCommand

from apps.departments.models import Department, Position


class Command(BaseCommand):
    help = "Создать тестовую структуру подразделений университета"

    def handle(self, *args, **kwargs) -> None:
        self.stdout.write("Создание подразделений...")

        # Ректорат
        rectorate, _ = Department.objects.get_or_create(
            code="REC",
            defaults={
                "name": {
                    "ru": "Ректорат",
                    "uz": "Rektorat",
                    "en": "Rectorate",
                },
                "department_type": Department.DepartmentType.RECTORATE,
            },
        )

        # Факультеты
        faculties_data = [
            (
                "FAC-CS",
                {
                    "ru": "Факультет компьютерных наук",
                    "uz": "Kompyuter fanlari fakulteti",
                    "en": "Faculty of Computer Science",
                },
                Department.DepartmentType.FACULTY,
            ),
            (
                "FAC-ECO",
                {
                    "ru": "Экономический факультет",
                    "uz": "Iqtisodiyot fakulteti",
                    "en": "Faculty of Economics",
                },
                Department.DepartmentType.FACULTY,
            ),
            (
                "FAC-LAW",
                {
                    "ru": "Юридический факультет",
                    "uz": "Huquq fakulteti",
                    "en": "Faculty of Law",
                },
                Department.DepartmentType.FACULTY,
            ),
        ]

        faculties = {}
        for code, name, dept_type in faculties_data:
            dept, _ = Department.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "department_type": dept_type,
                    "parent": rectorate,
                },
            )
            faculties[code] = dept

        # Кафедры факультета CS
        departments_data = [
            (
                "DEP-CS-SW",
                {
                    "ru": "Кафедра программной инженерии",
                    "uz": "Dasturiy injiniring kafedrasi",
                    "en": "Software Engineering Department",
                },
                faculties["FAC-CS"],
            ),
            (
                "DEP-CS-AI",
                {
                    "ru": "Кафедра искусственного интеллекта",
                    "uz": "Sun'iy intellekt kafedrasi",
                    "en": "AI Department",
                },
                faculties["FAC-CS"],
            ),
            (
                "DEP-ECO-FIN",
                {
                    "ru": "Кафедра финансов",
                    "uz": "Moliya kafedrasi",
                    "en": "Finance Department",
                },
                faculties["FAC-ECO"],
            ),
        ]
        for code, name, parent in departments_data:
            Department.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "department_type": Department.DepartmentType.DEPARTMENT,
                    "parent": parent,
                },
            )

        # Административные службы
        admin_data = [
            (
                "HR",
                {
                    "ru": "Отдел кадров",
                    "uz": "Kadrlar bo'limi",
                    "en": "HR Department",
                },
                Department.DepartmentType.ADMIN_SERVICE,
            ),
            (
                "FIN",
                {
                    "ru": "Финансовый отдел",
                    "uz": "Moliya bo'limi",
                    "en": "Finance Department",
                },
                Department.DepartmentType.ADMIN_SERVICE,
            ),
            (
                "IT",
                {
                    "ru": "IT отдел",
                    "uz": "IT bo'lim",
                    "en": "IT Department",
                },
                Department.DepartmentType.SUPPORT_UNIT,
            ),
        ]
        for code, name, dept_type in admin_data:
            Department.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "department_type": dept_type,
                    "parent": rectorate,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(f"Создано подразделений: {Department.objects.count()}")
        )

        # Должности
        positions_data = [
            (
                "PROF",
                {
                    "ru": "Профессор",
                    "uz": "Professor",
                    "en": "Professor",
                },
                "PPS",
                True,
            ),
            (
                "ASSOC",
                {
                    "ru": "Доцент",
                    "uz": "Dotsent",
                    "en": "Associate Professor",
                },
                "PPS",
                True,
            ),
            (
                "ASSIST",
                {
                    "ru": "Ассистент",
                    "uz": "Assistent",
                    "en": "Assistant",
                },
                "PPS",
                True,
            ),
            (
                "RECTOR",
                {"ru": "Ректор", "uz": "Rektor", "en": "Rector"},
                "AUP",
                False,
            ),
            (
                "VICE_RECTOR",
                {
                    "ru": "Проректор",
                    "uz": "Prorektor",
                    "en": "Vice Rector",
                },
                "AUP",
                False,
            ),
            (
                "HEAD_DEPT",
                {
                    "ru": "Заведующий кафедрой",
                    "uz": "Kafedra mudiri",
                    "en": "Head of Department",
                },
                "AUP",
                True,
            ),
            (
                "HR_SPEC",
                {
                    "ru": "Специалист по кадрам",
                    "uz": "Kadrlar bo'yicha mutaxassis",
                    "en": "HR Specialist",
                },
                "AUP",
                False,
            ),
            (
                "ACCOUNTANT",
                {
                    "ru": "Бухгалтер",
                    "uz": "Hisobchi",
                    "en": "Accountant",
                },
                "AUP",
                False,
            ),
        ]
        for code, name, category, is_academic in positions_data:
            Position.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "category": category,
                    "is_academic": is_academic,
                },
            )

        self.stdout.write(self.style.SUCCESS(f"Создано должностей: {Position.objects.count()}"))
        self.stdout.write(self.style.SUCCESS("Seed завершён!"))
