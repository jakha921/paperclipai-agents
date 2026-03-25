"""Команда заполнения БД реалистичными демо-данными."""

from __future__ import annotations

import random
from datetime import date, datetime, time
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()

PASSWORD = "Admin123!"

# ---------------------------------------------------------------------------
# Вспомогательные данные
# ---------------------------------------------------------------------------

FIRST_NAMES_M = ["Алишер", "Бобур", "Давронбек", "Фирдавс", "Жасур", "Камол", "Лазиз", "Мирзохид"]
FIRST_NAMES_F = ["Нилуфар", "Ойдин", "Зулайхо", "Гулнора", "Феруза", "Дилноза"]
LAST_NAMES = [
    "Каримов",
    "Рахимов",
    "Усмонов",
    "Хасанов",
    "Юсупов",
    "Тошматов",
    "Назаров",
    "Холиқов",
    "Исмоилов",
    "Абдуллаев",
    "Мирзаев",
    "Бекмуродов",
    "Сайдалиев",
    "Қодиров",
    "Норматов",
]


def _pinfl(n: int) -> str:
    return f"1000{n:010d}"


def _inn(n: int) -> str:
    return f"100{n:06d}"


def _passport(n: int) -> str:
    return f"AB{n:07d}"


def _phone(n: int) -> str:
    return f"+99890{n:07d}"


def _emp_num(n: int) -> str:
    return f"EMP-{n:04d}"


# ---------------------------------------------------------------------------
# Команда
# ---------------------------------------------------------------------------


class Command(BaseCommand):
    help = "Заполнить БД реалистичными демо-данными (employees, leaves, attendance, payroll и др.)"

    def handle(self, *args, **options) -> None:  # noqa: C901
        self.stdout.write("=== seed_demo: создание демо-данных ===")

        employees = self._create_employees()
        self._create_employee_salaries(employees)
        tax_cfg = self._ensure_tax_config_2026()
        self._create_leave_requests(employees)
        self._create_attendance_records(employees)
        self._create_payrolls(employees, tax_cfg)
        self._create_recruitment()
        self._create_appraisal(employees)
        self._create_training(employees)
        self._create_academic_data(employees)

        self.stdout.write(self.style.SUCCESS("=== seed_demo завершён ==="))

    # ------------------------------------------------------------------
    # 1. Сотрудники
    # ------------------------------------------------------------------

    def _create_employees(self):  # noqa: C901
        from apps.departments.models import Department, Employee, Position

        self.stdout.write("  Создание сотрудников...")

        dept_by_code = {d.code: d for d in Department.objects.all()}
        pos_by_code = {p.code: p for p in Position.objects.all()}

        # Карта: email → (dept_code, pos_code, first, last, gender)
        linked_users_data = [
            ("superuser@uni-hrm.uz", "REC", "RECTOR", "Акмаль", "Каримов", "MALE"),
            ("admin@uni-hrm.uz", "IT", "HR_SPEC", "Шерзод", "Абдуллаев", "MALE"),
            ("hr@uni-hrm.uz", "HR", "HR_SPEC", "Нилуфар", "Рахимова", "FEMALE"),
            ("dean@uni-hrm.uz", "FAC-CS", "HEAD_DEPT", "Баходир", "Усмонов", "MALE"),
            ("head@uni-hrm.uz", "DEP-CS-SW", "HEAD_DEPT", "Зафар", "Хасанов", "MALE"),
            ("accountant@uni-hrm.uz", "FIN", "ACCOUNTANT", "Феруза", "Юсупова", "FEMALE"),
            ("employee@uni-hrm.uz", "DEP-CS-SW", "ASSIST", "Жасур", "Тошматов", "MALE"),
        ]

        # Дополнительные сотрудники без связанных пользователей
        extra_data = [
            ("DEP-CS-SW", "PROF", "Алишер", "Назаров", "MALE"),
            ("DEP-CS-AI", "ASSOC", "Бобур", "Холиқов", "MALE"),
            ("DEP-CS-AI", "ASSIST", "Ойдин", "Исмоилова", "FEMALE"),
            ("DEP-ECO-FIN", "PROF", "Камол", "Мирзаев", "MALE"),
            ("DEP-ECO-FIN", "ASSOC", "Гулнора", "Бекмуродова", "FEMALE"),
            ("DEP-CS-SW", "ASSIST", "Лазиз", "Сайдалиев", "MALE"),
            ("HR", "HR_SPEC", "Дилноза", "Қодирова", "FEMALE"),
            ("DEP-ECO-FIN", "ASSIST", "Фирдавс", "Норматов", "MALE"),
        ]

        employees = []
        seq = 1  # sequence for unique fields

        for email, dept_code, pos_code, first, last, gender in linked_users_data:
            dept = dept_by_code.get(dept_code)
            pos = pos_by_code.get(pos_code)
            if not dept or not pos:
                self.stdout.write(
                    self.style.WARNING(f"    Пропуск {email}: dept={dept_code} pos={pos_code}")
                )
                continue

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"    Пользователь {email} не найден"))
                continue

            # Проверяем — может Employee уже есть у этого пользователя
            if hasattr(user, "employee") and user.employee is not None:
                employees.append(user.employee)
                self.stdout.write(f"    Существует: {user.employee}")
                seq += 1
                continue

            emp, created = Employee.objects.get_or_create(
                employee_number=_emp_num(seq),
                defaults={
                    "user": user,
                    "department": dept,
                    "position": pos,
                    "first_name": first,
                    "last_name": last,
                    "gender": gender,
                    "birth_date": date(1975 + seq, (seq % 12) + 1, min(seq + 1, 28)),
                    "hire_date": date(2018 + (seq % 5), (seq % 12) + 1, min(seq * 2, 28)),
                    "nationality": "Узбек",
                    "pinfl": _pinfl(seq),
                    "inn": _inn(seq),
                    "passport_series": _passport(seq),
                    "phone": _phone(seq),
                    "email": email,
                    "status": "ACTIVE",
                },
            )
            if created:
                self.stdout.write(f"    Создан: {emp}")
            employees.append(emp)
            seq += 1

        for dept_code, pos_code, first, last, gender in extra_data:
            dept = dept_by_code.get(dept_code)
            pos = pos_by_code.get(pos_code)
            if not dept or not pos:
                continue

            # Для новых сотрудников создаём User
            extra_email = f"demo{seq}@uni-hrm.uz"
            user, _ = User.objects.get_or_create(
                email=extra_email,
                defaults={
                    "username": f"demo{seq}",
                    "first_name": first,
                    "last_name": last,
                    "is_verified": True,
                },
            )
            if not user.has_usable_password():
                user.set_password(PASSWORD)
                user.save(update_fields=["password"])

            # Проверяем Employee
            if hasattr(user, "employee") and user.employee is not None:
                employees.append(user.employee)
                self.stdout.write(f"    Существует: {user.employee}")
                seq += 1
                continue

            emp, created = Employee.objects.get_or_create(
                employee_number=_emp_num(seq),
                defaults={
                    "user": user,
                    "department": dept,
                    "position": pos,
                    "first_name": first,
                    "last_name": last,
                    "gender": gender,
                    "birth_date": date(1978 + (seq % 20), (seq % 12) + 1, min(seq % 27 + 1, 28)),
                    "hire_date": date(2019 + (seq % 4), (seq % 12) + 1, min(seq % 27 + 1, 28)),
                    "nationality": "Узбек",
                    "pinfl": _pinfl(seq),
                    "inn": _inn(seq),
                    "passport_series": _passport(seq),
                    "phone": _phone(seq),
                    "email": extra_email,
                    "status": "ACTIVE",
                },
            )
            if created:
                self.stdout.write(f"    Создан: {emp}")
            employees.append(emp)
            seq += 1

        self.stdout.write(self.style.SUCCESS(f"  Сотрудников: {len(employees)}"))
        return employees

    # ------------------------------------------------------------------
    # 2. Зарплаты
    # ------------------------------------------------------------------

    def _create_employee_salaries(self, employees: list) -> None:
        from apps.payroll.models import EmployeeSalary

        self.stdout.write("  Создание зарплат...")
        base_salaries = [
            5_000_000,
            4_500_000,
            3_800_000,
            6_000_000,
            5_500_000,
            4_200_000,
            3_500_000,
            7_000_000,
            5_800_000,
            4_800_000,
            6_500_000,
            5_200_000,
            4_000_000,
            3_600_000,
            3_800_000,
        ]
        count = 0
        for i, emp in enumerate(employees):
            base = Decimal(str(base_salaries[i % len(base_salaries)]))
            _, created = EmployeeSalary.objects.get_or_create(
                employee=emp,
                effective_from=date(2025, 1, 1),
                defaults={
                    "base_salary": base,
                    "academic_bonus_pct": Decimal("15") if i % 3 == 0 else Decimal("0"),
                    "position_bonus_pct": Decimal("10"),
                    "seniority_bonus_pct": Decimal("5") if i % 2 == 0 else Decimal("0"),
                    "is_active": True,
                },
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f"  Зарплат создано: {count}"))

    # ------------------------------------------------------------------
    # 3. Налоговая конфигурация 2026
    # ------------------------------------------------------------------

    def _ensure_tax_config_2026(self):
        from apps.payroll.models import TaxConfiguration

        cfg, created = TaxConfiguration.objects.get_or_create(
            year=2026,
            defaults={
                "ndfl_rate": Decimal("0.12"),
                "social_tax_rate": Decimal("0.12"),
                "inps_employee_rate": Decimal("0.001"),
                "inps_employer_rate": Decimal("0.001"),
                "minimum_wage": Decimal("1300000"),
            },
        )
        if created:
            self.stdout.write("  TaxConfig 2026 создан")
        return cfg

    # ------------------------------------------------------------------
    # 4. Заявки на отпуск
    # ------------------------------------------------------------------

    def _create_leave_requests(self, employees: list) -> None:
        from apps.leaves.models import LeaveRequest, LeaveType

        self.stdout.write("  Создание заявок на отпуск...")

        leave_types = list(LeaveType.objects.all())
        if not leave_types:
            self.stdout.write(self.style.WARNING("  Типы отпусков не найдены, пропуск"))
            return

        annual_types = [lt for lt in leave_types if "ANNUAL" in lt.code or "SICK" in lt.code]
        if not annual_types:
            annual_types = leave_types[:2]

        hr_user = None
        try:
            from apps.accounts.models import User as AuthUser

            hr_user = AuthUser.objects.get(email="hr@uni-hrm.uz")
        except Exception:
            pass

        requests_data = [
            # (emp_idx, leave_type_code_prefix, start, end, status, rejection_reason)
            # Approved — прошлые периоды
            (0, "ANNUAL", date(2025, 7, 1), date(2025, 7, 14), "APPROVED", ""),
            (1, "ANNUAL", date(2025, 8, 1), date(2025, 8, 7), "APPROVED", ""),
            (2, "SICK", date(2025, 9, 10), date(2025, 9, 15), "APPROVED", ""),
            (3, "ANNUAL", date(2025, 10, 1), date(2025, 10, 7), "APPROVED", ""),
            (4, "ANNUAL", date(2025, 11, 1), date(2025, 11, 10), "APPROVED", ""),
            (5, "ANNUAL", date(2025, 12, 15), date(2025, 12, 25), "APPROVED", ""),
            (6, "SICK", date(2026, 1, 5), date(2026, 1, 8), "APPROVED", ""),
            (7, "ANNUAL", date(2026, 1, 20), date(2026, 1, 31), "APPROVED", ""),
            # Pending — ждут одобрения
            (0, "ANNUAL", date(2026, 4, 1), date(2026, 4, 14), "PENDING_HR", ""),
            (2, "ANNUAL", date(2026, 5, 1), date(2026, 5, 10), "PENDING_HEAD", ""),
            (4, "SICK", date(2026, 4, 20), date(2026, 4, 25), "PENDING_HR", ""),
            (6, "ANNUAL", date(2026, 6, 1), date(2026, 6, 7), "PENDING_HEAD", ""),
            (8, "ANNUAL", date(2026, 5, 15), date(2026, 5, 22), "PENDING_HR", ""),
            # Rejected
            (
                1,
                "ANNUAL",
                date(2026, 2, 10),
                date(2026, 2, 20),
                "REJECTED",
                "Производственная необходимость",
            ),
            (
                3,
                "SICK",
                date(2026, 2, 15),
                date(2026, 2, 18),
                "REJECTED",
                "Не предоставлен больничный лист",
            ),
            (5, "ANNUAL", date(2026, 3, 1), date(2026, 3, 5), "REJECTED", "Высокая загруженность"),
            (
                7,
                "ANNUAL",
                date(2026, 3, 10),
                date(2026, 3, 14),
                "REJECTED",
                "Пересечение с отпуском коллеги",
            ),
            # Текущий месяц (март 2026)
            (9, "SICK", date(2026, 3, 5), date(2026, 3, 7), "APPROVED", ""),
            (10, "ANNUAL", date(2026, 3, 18), date(2026, 3, 22), "PENDING_HR", ""),
            (11, "ANNUAL", date(2026, 3, 25), date(2026, 3, 31), "PENDING_HEAD", ""),
        ]

        count = 0
        for emp_idx, leave_prefix, start, end, status, rejection in requests_data:
            if emp_idx >= len(employees):
                continue
            emp = employees[emp_idx]

            # Найти подходящий тип отпуска
            lt = next(
                (t for t in leave_types if leave_prefix in t.code),
                leave_types[0],
            )
            days = (end - start).days + 1

            # Проверяем нет ли дубликата
            existing = LeaveRequest.objects.filter(
                employee=emp, start_date=start, leave_type=lt
            ).first()
            if existing:
                continue

            lr = LeaveRequest.objects.create(
                employee=emp,
                leave_type=lt,
                start_date=start,
                end_date=end,
                days_count=days,
                reason=f"Заявка на {lt.code} отпуск",
                status=status,
                rejection_reason=rejection,
                approved_by=hr_user if status == "APPROVED" else None,
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"  Заявок на отпуск создано: {count}"))

    # ------------------------------------------------------------------
    # 5. Записи посещаемости
    # ------------------------------------------------------------------

    def _create_attendance_records(self, employees: list) -> None:
        from apps.attendance.models import AttendanceRecord

        self.stdout.write("  Создание записей посещаемости...")

        # Текущий месяц: март 2026 (первые 18 рабочих дней)
        march_days = [
            date(2026, 3, d)
            for d in range(1, 20)  # 1–19 марта
            if date(2026, 3, d).weekday() < 5  # только будни
        ]

        # Берём первых 6 сотрудников
        target_employees = employees[:6]
        count = 0

        # Также добавим несколько записей за январь-февраль для зарплатного расчёта
        jan_days = [date(2026, 1, d) for d in range(2, 22) if date(2026, 1, d).weekday() < 5][:10]

        feb_days = [date(2026, 2, d) for d in range(2, 23) if date(2026, 2, d).weekday() < 5][:10]

        for emp in target_employees:
            for work_date in march_days + jan_days + feb_days:
                if AttendanceRecord.objects.filter(employee=emp, date=work_date).exists():
                    continue

                # Иногда опаздывают, иногда отсутствуют
                rnd = random.random()
                if rnd < 0.05:
                    status = "ABSENT"
                    check_in = None
                    check_out = None
                    worked = Decimal("0.00")
                elif rnd < 0.15:
                    status = "LATE"
                    check_in = time(9, random.randint(30, 59))
                    check_out = time(18, random.randint(0, 30))
                    worked = Decimal("7.50")
                else:
                    status = "PRESENT"
                    check_in = time(8, random.randint(45, 59))
                    check_out = time(17, random.randint(45, 59))
                    worked = Decimal("9.00")

                overtime = Decimal("1.50") if random.random() < 0.1 else Decimal("0.00")

                AttendanceRecord.objects.create(
                    employee=emp,
                    date=work_date,
                    check_in=check_in,
                    check_out=check_out,
                    status=status,
                    worked_hours=worked,
                    overtime_hours=overtime,
                    source="MANUAL",
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"  Записей посещаемости создано: {count}"))

    # ------------------------------------------------------------------
    # 6. Расчётные листы (payroll)
    # ------------------------------------------------------------------

    def _create_payrolls(self, employees: list, tax_cfg) -> None:
        from apps.payroll.models import EmployeeSalary, Payroll

        self.stdout.write("  Создание расчётных листов...")

        target = employees[:6]
        months = [(1, 2026), (2, 2026)]
        count = 0

        for emp in target:
            salary_obj = EmployeeSalary.objects.filter(employee=emp, is_active=True).first()
            if not salary_obj:
                continue

            gross_monthly = salary_obj.gross_monthly
            base = salary_obj.base_salary
            academic_b = base * salary_obj.academic_bonus_pct / Decimal("100")
            position_b = base * salary_obj.position_bonus_pct / Decimal("100")
            seniority_b = base * salary_obj.seniority_bonus_pct / Decimal("100")

            for month, year in months:
                existing = Payroll.objects.filter(employee=emp, month=month, year=year).first()
                if existing:
                    continue

                # Рабочих дней в месяце
                if month == 1:
                    working_days = 21
                else:
                    working_days = 20

                days_worked = working_days - random.randint(0, 2)
                days_absent = working_days - days_worked
                attendance_ratio = Decimal(str(days_worked)) / Decimal(str(working_days))

                gross = (gross_monthly * attendance_ratio).quantize(Decimal("0.01"))
                ndfl = (gross * tax_cfg.ndfl_rate).quantize(Decimal("0.01"))
                inps_emp = (gross * tax_cfg.inps_employee_rate).quantize(Decimal("0.01"))
                total_deductions = ndfl + inps_emp
                net = gross - total_deductions
                employer_social_tax = (gross * tax_cfg.social_tax_rate).quantize(Decimal("0.01"))
                employer_inps = (gross * tax_cfg.inps_employer_rate).quantize(Decimal("0.01"))

                Payroll.objects.create(
                    employee=emp,
                    month=month,
                    year=year,
                    tax_config=tax_cfg,
                    base_salary=base,
                    academic_bonus=academic_b.quantize(Decimal("0.01")),
                    position_bonus=position_b.quantize(Decimal("0.01")),
                    seniority_bonus=seniority_b.quantize(Decimal("0.01")),
                    other_allowances=salary_obj.other_allowances,
                    working_days_in_month=working_days,
                    days_worked=days_worked,
                    days_on_leave=0,
                    days_absent=days_absent,
                    overtime_hours=Decimal("0"),
                    attendance_ratio=attendance_ratio.quantize(Decimal("0.0001")),
                    overtime_payment=Decimal("0"),
                    gross_salary=gross,
                    ndfl=ndfl,
                    inps_employee=inps_emp,
                    other_deductions=Decimal("0"),
                    total_deductions=total_deductions,
                    net_salary=net,
                    employer_social_tax=employer_social_tax,
                    employer_inps=employer_inps,
                    status="PAID" if month == 1 else "APPROVED",
                    paid_date=date(2026, month + 1, 5) if month == 1 else None,
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f"  Расчётных листов создано: {count}"))

    # ------------------------------------------------------------------
    # 7. Рекрутинг
    # ------------------------------------------------------------------

    def _create_recruitment(self) -> None:
        from apps.departments.models import Department, Position
        from apps.recruitment.models import Candidate, Interview, Vacancy

        self.stdout.write("  Создание вакансий и кандидатов...")

        try:
            dept_sw = Department.objects.get(code="DEP-CS-SW")
            dept_eco = Department.objects.get(code="DEP-ECO-FIN")
            pos_assist = Position.objects.get(code="ASSIST")
            pos_assoc = Position.objects.get(code="ASSOC")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  Пропуск рекрутинга: {e}"))
            return

        vac1, _ = Vacancy.objects.get_or_create(
            title={"ru": "Ассистент кафедры программной инженерии", "en": "SE Assistant"},
            defaults={
                "position": pos_assist,
                "department": dept_sw,
                "requirements": "Высшее образование в области IT, опыт преподавания желателен",
                "responsibilities": "Проведение практических занятий, научная деятельность",
                "status": "OPEN",
                "vacancies_count": 2,
                "deadline": date(2026, 4, 30),
            },
        )

        vac2, _ = Vacancy.objects.get_or_create(
            title={"ru": "Доцент кафедры финансов", "en": "Finance Associate Professor"},
            defaults={
                "position": pos_assoc,
                "department": dept_eco,
                "requirements": "Учёная степень PhD/кандидат наук, публикации в WoS/Scopus",
                "responsibilities": "Чтение лекций, руководство аспирантами",
                "status": "OPEN",
                "vacancies_count": 1,
                "deadline": date(2026, 5, 15),
            },
        )

        candidates_data = [
            # (vacancy, first, last, phone, email, source, stage)
            (
                vac1,
                "Санжар",
                "Матмусаев",
                "+998901111001",
                "sanjarm@mail.ru",
                "EXTERNAL",
                "APPLIED",
            ),
            (
                vac1,
                "Умид",
                "Давлатов",
                "+998901111002",
                "umid.d@gmail.com",
                "EXTERNAL",
                "SCREENING",
            ),
            (
                vac1,
                "Зафар",
                "Шарипов",
                "+998901111003",
                "zafar.s@yahoo.com",
                "REFERRAL",
                "INTERVIEW",
            ),
            (vac2, "Моҳира", "Ҳасанова", "+998901111004", "mohira.h@edu.uz", "EXTERNAL", "APPLIED"),
            (vac2, "Тимур", "Эргашев", "+998901111005", "timur.e@uni.uz", "HEMIS", "OFFER"),
        ]

        count_cand = 0
        for vac, first, last, phone, email, source, stage in candidates_data:
            _, created = Candidate.objects.get_or_create(
                vacancy=vac,
                email=email,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "phone": phone,
                    "source": source,
                    "stage": stage,
                    "notes": f"Кандидат {first} {last} — {source}",
                },
            )
            if created:
                count_cand += 1

        # Интервью для кандидата на стадии INTERVIEW
        interview_cand = Candidate.objects.filter(stage="INTERVIEW", vacancy=vac1).first()
        if interview_cand:
            hr_user = None
            try:
                hr_user = User.objects.get(email="hr@uni-hrm.uz")
            except User.DoesNotExist:
                pass
            if hr_user:
                Interview.objects.get_or_create(
                    candidate=interview_cand,
                    interview_type="HR",
                    defaults={
                        "interviewer": hr_user,
                        "scheduled_at": timezone.make_aware(datetime(2026, 3, 20, 10, 0)),
                        "result": "PENDING",
                        "duration_minutes": 45,
                        "notes": "HR-интервью по вакансии ассистента",
                    },
                )

        self.stdout.write(self.style.SUCCESS(f"  Вакансий: 2, Кандидатов создано: {count_cand}"))

    # ------------------------------------------------------------------
    # 8. Аттестация
    # ------------------------------------------------------------------

    def _create_appraisal(self, employees: list) -> None:
        from apps.appraisal.models import AppraisalCycle, EmployeeAppraisal, KPIIndicator

        self.stdout.write("  Создание аттестации...")

        cycle, _ = AppraisalCycle.objects.get_or_create(
            name="Аттестация 2025-2026 учебный год",
            defaults={
                "start_date": date(2025, 9, 1),
                "end_date": date(2026, 6, 30),
                "status": "active",
            },
        )

        kpis_data = [
            (
                "academic",
                "Учебная нагрузка",
                "Выполнение учебной нагрузки согласно плану",
                Decimal("30"),
                10,
            ),
            (
                "research",
                "Научные публикации",
                "Количество статей WoS/Scopus/РИНЦ",
                Decimal("25"),
                10,
            ),
            (
                "administrative",
                "Административная активность",
                "Участие в работе кафедры/факультета",
                Decimal("20"),
                10,
            ),
            (
                "service",
                "Работа со студентами",
                "Научное руководство, кружки, олимпиады",
                Decimal("15"),
                10,
            ),
            (
                "academic",
                "Повышение квалификации",
                "Курсы, тренинги, конференции",
                Decimal("10"),
                10,
            ),
        ]

        kpis = []
        for category, name_ru, desc, weight, max_score in kpis_data:
            kpi, _ = KPIIndicator.objects.get_or_create(
                name={"ru": name_ru, "en": name_ru},
                category=category,
                defaults={"description": desc, "weight": weight, "max_score": max_score},
            )
            kpis.append(kpi)

        # Аттестации для первых 5 сотрудников
        target = employees[:5]
        reviewer = employees[0] if employees else None
        count_appr = 0

        for i, emp in enumerate(target):
            _, created = EmployeeAppraisal.objects.get_or_create(
                cycle=cycle,
                employee=emp,
                defaults={
                    "reviewer": reviewer if emp != reviewer else None,
                    "status": [
                        "pending",
                        "self_review",
                        "manager_review",
                        "completed",
                        "completed",
                    ][i % 5],
                    "overall_score": Decimal("8.50") if i % 2 == 0 else None,
                    "comments": "Хорошие результаты по всем показателям" if i % 2 == 0 else "",
                },
            )
            if created:
                count_appr += 1

        self.stdout.write(
            self.style.SUCCESS(f"  Цикл аттестации: 1, KPI: {len(kpis)}, Аттестаций: {count_appr}")
        )

    # ------------------------------------------------------------------
    # 9. Обучение
    # ------------------------------------------------------------------

    def _create_training(self, employees: list) -> None:
        from apps.appraisal.models import TrainingProgram, TrainingRecord

        self.stdout.write("  Создание программ обучения...")

        prog1, _ = TrainingProgram.objects.get_or_create(
            name={
                "ru": "Методика преподавания в высшей школе",
                "en": "Higher Education Teaching Methods",
            },
            defaults={
                "description": "Курс повышения педагогической квалификации для ППС",
                "provider": "Институт переподготовки кадров при МВО",
                "training_type": "internal",
                "duration_hours": 72,
                "cost": Decimal("500000"),
                "is_active": True,
            },
        )

        prog2, _ = TrainingProgram.objects.get_or_create(
            name={"ru": "Python для анализа данных", "en": "Python for Data Analysis"},
            defaults={
                "description": "Онлайн курс по Data Science и ML",
                "provider": "Coursera / Внутренний",
                "training_type": "online",
                "duration_hours": 40,
                "cost": Decimal("0"),
                "is_active": True,
            },
        )

        records_data = [
            (
                employees[0] if employees else None,
                prog1,
                date(2026, 1, 15),
                date(2026, 2, 15),
                "completed",
                "CERT-2026-001",
                92,
            ),
            (
                employees[1] if len(employees) > 1 else None,
                prog1,
                date(2026, 2, 1),
                date(2026, 3, 1),
                "in_progress",
                "",
                None,
            ),
            (
                employees[2] if len(employees) > 2 else None,
                prog2,
                date(2026, 3, 1),
                date(2026, 4, 30),
                "enrolled",
                "",
                None,
            ),
        ]

        count = 0
        for emp, prog, start, end, status, cert, score in records_data:
            if emp is None:
                continue
            _, created = TrainingRecord.objects.get_or_create(
                employee=emp,
                program=prog,
                defaults={
                    "start_date": start,
                    "end_date": end,
                    "status": status,
                    "certificate_number": cert,
                    "score": score,
                },
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"  Программ обучения: 2, Записей: {count}"))

    # ------------------------------------------------------------------
    # 10. Академические данные
    # ------------------------------------------------------------------

    def _create_academic_data(self, employees: list) -> None:
        from apps.academic.models import (
            AcademicDegree,
            AcademicLoad,
            AcademicTitle,
            EmployeeAcademic,
            Subject,
        )
        from apps.departments.models import Department

        self.stdout.write("  Создание академических данных...")

        phd = AcademicDegree.objects.filter(code="PHD").first()
        dsc = AcademicDegree.objects.filter(code="DSC").first()
        docent_title = AcademicTitle.objects.filter(code="DOCENT").first()
        prof_title = AcademicTitle.objects.filter(code="PROFESSOR").first()

        # Академические данные для первых 4 сотрудников с академическими позициями
        academic_employees = [e for e in employees if e.position and e.position.is_academic][:4]

        academic_data = [
            (
                phd,
                docent_title,
                "Информационные системы",
                "Оптимизация алгоритмов ML",
                "ДД-2020-001",
                date(2020, 6, 15),
            ),
            (
                dsc,
                prof_title,
                "Искусственный интеллект",
                "Глубокое обучение в NLP",
                "ДД-2018-042",
                date(2018, 9, 1),
            ),
            (
                phd,
                None,
                "Программная инженерия",
                "Методы верификации ПО",
                "ДД-2022-015",
                date(2022, 3, 20),
            ),
            (
                phd,
                docent_title,
                "Финансы и кредит",
                "Моделирование финансовых рисков",
                "ДД-2019-088",
                date(2019, 11, 10),
            ),
        ]

        emp_acad_count = 0
        for i, emp in enumerate(academic_employees):
            if i >= len(academic_data):
                break
            degree, title, spec, dissertation, diploma, awarded = academic_data[i]
            _, created = EmployeeAcademic.objects.get_or_create(
                employee=emp,
                defaults={
                    "degree": degree,
                    "title": title,
                    "specialization": spec,
                    "dissertation_topic": dissertation,
                    "diploma_number": diploma,
                    "awarded_date": awarded,
                },
            )
            if created:
                emp_acad_count += 1

        # Дисциплины и нагрузка
        try:
            dept_sw = Department.objects.get(code="DEP-CS-SW")
            dept_ai = Department.objects.get(code="DEP-CS-AI")
        except Department.DoesNotExist:
            self.stdout.write(self.style.SUCCESS(f"  EmployeeAcademic создано: {emp_acad_count}"))
            return

        subjects_data = [
            (
                "CS101",
                {"ru": "Введение в программирование", "en": "Introduction to Programming"},
                dept_sw,
                5,
            ),
            (
                "CS202",
                {"ru": "Алгоритмы и структуры данных", "en": "Algorithms and Data Structures"},
                dept_sw,
                6,
            ),
            ("AI301", {"ru": "Машинное обучение", "en": "Machine Learning"}, dept_ai, 6),
            (
                "AI201",
                {"ru": "Искусственный интеллект", "en": "Artificial Intelligence"},
                dept_ai,
                5,
            ),
        ]

        subjects = []
        for code, name, dept, credits in subjects_data:
            subj, _ = Subject.objects.get_or_create(
                code=code,
                defaults={"name": name, "department": dept, "credits": credits},
            )
            subjects.append(subj)

        # Нагрузка для первых 3 академических сотрудников
        load_count = 0
        load_assignments = [
            (0, 0, "2025-2026", 1, 30, 15, 0),  # emp0, CS101, sem1
            (0, 1, "2025-2026", 2, 28, 14, 0),  # emp0, CS202, sem2
            (1, 2, "2025-2026", 1, 32, 0, 16),  # emp1, AI301, sem1
            (2, 3, "2025-2026", 1, 30, 15, 15),  # emp2, AI201, sem1
        ]

        for emp_i, subj_i, acad_year, sem, lec, sem_h, lab in load_assignments:
            if emp_i >= len(academic_employees) or subj_i >= len(subjects):
                continue
            emp = academic_employees[emp_i]
            subj = subjects[subj_i]
            _, created = AcademicLoad.objects.get_or_create(
                employee=emp,
                subject=subj,
                academic_year=acad_year,
                semester=sem,
                defaults={
                    "lecture_hours": lec,
                    "seminar_hours": sem_h,
                    "lab_hours": lab,
                    "load_type": "PRIMARY",
                },
            )
            if created:
                load_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"  EmployeeAcademic: {emp_acad_count}, Дисциплин: {len(subjects)}, Нагрузок: {load_count}"
            )
        )
