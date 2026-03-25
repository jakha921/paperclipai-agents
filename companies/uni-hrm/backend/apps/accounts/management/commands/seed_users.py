from django.core.management.base import BaseCommand

from apps.accounts.models import Role, User, UserRole

USERS = [
    {
        "email": "superuser@uni-hrm.uz",
        "username": "superuser",
        "first_name": "Super",
        "last_name": "Admin",
        "is_superuser": True,
        "is_staff": True,
        "role_code": None,
    },
    {
        "email": "admin@uni-hrm.uz",
        "username": "admin",
        "first_name": "Админ",
        "last_name": "Системный",
        "is_superuser": False,
        "is_staff": True,
        "role_code": "admin",
    },
    {
        "email": "hr@uni-hrm.uz",
        "username": "hr",
        "first_name": "HR",
        "last_name": "Менеджер",
        "is_superuser": False,
        "is_staff": False,
        "role_code": "hr_manager",
    },
    {
        "email": "dean@uni-hrm.uz",
        "username": "dean",
        "first_name": "Декан",
        "last_name": "Факультета",
        "is_superuser": False,
        "is_staff": False,
        "role_code": "dean",
    },
    {
        "email": "head@uni-hrm.uz",
        "username": "head",
        "first_name": "Заведующий",
        "last_name": "Кафедрой",
        "is_superuser": False,
        "is_staff": False,
        "role_code": "head_of_department",
    },
    {
        "email": "accountant@uni-hrm.uz",
        "username": "accountant",
        "first_name": "Бухгалтер",
        "last_name": "Главный",
        "is_superuser": False,
        "is_staff": False,
        "role_code": "accountant",
    },
    {
        "email": "employee@uni-hrm.uz",
        "username": "employee",
        "first_name": "Сотрудник",
        "last_name": "Тестовый",
        "is_superuser": False,
        "is_staff": False,
        "role_code": "employee",
    },
]

PASSWORD = "Admin123!"


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей с ролями"

    def handle(self, *args, **options):
        for user_data in USERS:
            role_code = user_data.pop("role_code")
            email = user_data["email"]

            user, created = User.objects.get_or_create(
                email=email,
                defaults=user_data,
            )
            if created:
                user.set_password(PASSWORD)
                user.is_verified = True
                user.save(update_fields=["password", "is_verified"])

            if role_code:
                try:
                    role = Role.objects.get(code=role_code)
                    UserRole.objects.get_or_create(user=user, role=role)
                except Role.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f"  Роль '{role_code}' не найдена, пропускаем")
                    )

            action = "Создан" if created else "Существует"
            role_label = role_code or "superuser"
            self.stdout.write(f"  {action}: {email} ({role_label})")

            # Restore role_code for potential re-runs
            user_data["role_code"] = role_code

        self.stdout.write(self.style.SUCCESS("Тестовые пользователи созданы."))
