from django.core.management.base import BaseCommand

from apps.accounts.models import Permission, Role

PERMISSIONS = {
    "employees": [
        ("employees.view", "Просмотр сотрудников"),
        ("employees.create", "Создание сотрудников"),
        ("employees.edit", "Редактирование сотрудников"),
        ("employees.delete", "Удаление сотрудников"),
    ],
    "departments": [
        ("departments.view", "Просмотр департаментов"),
        ("departments.create", "Создание департаментов"),
        ("departments.edit", "Редактирование департаментов"),
        ("departments.delete", "Удаление департаментов"),
    ],
    "positions": [
        ("positions.view", "Просмотр должностей"),
        ("positions.create", "Создание должностей"),
        ("positions.edit", "Редактирование должностей"),
        ("positions.delete", "Удаление должностей"),
    ],
    "attendance": [
        ("attendance.view", "Просмотр посещаемости"),
        ("attendance.create", "Создание записей посещаемости"),
        ("attendance.edit", "Редактирование посещаемости"),
    ],
    "payroll": [
        ("payroll.view", "Просмотр зарплат"),
        ("payroll.create", "Создание начислений"),
        ("payroll.edit", "Редактирование начислений"),
        ("payroll.approve", "Утверждение начислений"),
    ],
    "documents": [
        ("documents.view", "Просмотр документов"),
        ("documents.create", "Создание документов"),
        ("documents.edit", "Редактирование документов"),
        ("documents.delete", "Удаление документов"),
    ],
    "reports": [
        ("reports.view", "Просмотр отчётов"),
        ("reports.export", "Экспорт отчётов"),
    ],
    "settings": [
        ("settings.view", "Просмотр настроек"),
        ("settings.edit", "Редактирование настроек"),
        ("roles.manage", "Управление ролями"),
        ("users.manage", "Управление пользователями"),
    ],
}

ROLES = {
    "super_admin": {
        "name": "Суперадминистратор",
        "level": "global",
        "description": "Полный доступ ко всей системе",
        "permissions": "__all__",
    },
    "admin": {
        "name": "Администратор",
        "level": "global",
        "description": "Управление системой без суперадминских функций",
        "permissions": "__all__",
    },
    "hr_manager": {
        "name": "HR менеджер",
        "level": "global",
        "description": "Управление персоналом",
        "permissions": [
            "employees.*",
            "departments.view",
            "positions.*",
            "attendance.*",
            "payroll.view",
            "documents.*",
            "reports.*",
        ],
    },
    "dean": {
        "name": "Декан",
        "level": "department",
        "description": "Управление факультетом",
        "permissions": [
            "employees.view",
            "departments.view",
            "positions.view",
            "attendance.view",
            "reports.view",
            "reports.export",
        ],
    },
    "head_of_department": {
        "name": "Заведующий кафедрой",
        "level": "department",
        "description": "Управление кафедрой",
        "permissions": [
            "employees.view",
            "departments.view",
            "positions.view",
            "attendance.view",
            "attendance.create",
            "reports.view",
        ],
    },
    "accountant": {
        "name": "Бухгалтер",
        "level": "global",
        "description": "Финансовые операции",
        "permissions": [
            "employees.view",
            "payroll.*",
            "reports.*",
        ],
    },
    "employee": {
        "name": "Сотрудник",
        "level": "personal",
        "description": "Базовый доступ сотрудника",
        "permissions": [
            "attendance.view",
            "documents.view",
            "payroll.view",
        ],
    },
    "external": {
        "name": "Внешний пользователь",
        "level": "personal",
        "description": "Ограниченный доступ",
        "permissions": [],
    },
}


def _resolve_permissions(patterns: list[str] | str, all_perms: dict[str, Permission]) -> list:
    """Разрешает паттерны разрешений в список объектов Permission."""
    if patterns == "__all__":
        return list(all_perms.values())

    result = []
    for pattern in patterns:
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            result.extend(p for code, p in all_perms.items() if code.startswith(prefix + "."))
        elif pattern in all_perms:
            result.append(all_perms[pattern])
    return result


class Command(BaseCommand):
    help = "Создаёт начальные роли и разрешения"

    def handle(self, *args, **options):
        # Создаём разрешения
        all_perms: dict[str, Permission] = {}
        for module, perms in PERMISSIONS.items():
            for codename, name in perms:
                perm, created = Permission.objects.get_or_create(
                    codename=codename,
                    defaults={"name": name, "module": module},
                )
                if not created:
                    perm.name = name
                    perm.module = module
                    perm.save(update_fields=["name", "module"])
                all_perms[codename] = perm

        self.stdout.write(f"Разрешений: {len(all_perms)}")

        # Создаём роли
        for code, config in ROLES.items():
            role, created = Role.objects.get_or_create(
                code=code,
                defaults={
                    "name": config["name"],
                    "level": config["level"],
                    "description": config["description"],
                },
            )
            if not created:
                role.name = config["name"]
                role.level = config["level"]
                role.description = config["description"]
                role.save(update_fields=["name", "level", "description"])

            perms = _resolve_permissions(config["permissions"], all_perms)
            role.permissions.set(perms)

            action = "Создана" if created else "Обновлена"
            self.stdout.write(f"  {action} роль: {role.name} ({len(perms)} разрешений)")

        self.stdout.write(self.style.SUCCESS("Роли и разрешения созданы успешно."))
