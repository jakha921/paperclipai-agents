# Архитектура uni-hrm

> Система управления кадрами (HRM) для университетов Узбекистана.
> Рассчитана на 500-2000 сотрудников.

---

## Оглавление

1. [Обзор системы](#1-обзор-системы)
2. [Структура монорепо](#2-структура-монорепо)
3. [Backend-архитектура](#3-backend-архитектура)
4. [Frontend-архитектура](#4-frontend-архитектура)
5. [RBAC-модель](#5-rbac-модель)
6. [API Versioning](#6-api-versioning)
7. [ERD-диаграмма](#7-erd-диаграмма)
8. [Deployment-архитектура](#8-deployment-архитектура)
9. [Security-архитектура](#9-security-архитектура)
10. [Интеграции](#10-интеграции)
11. [Стек технологий](#11-стек-технологий)

---

## 1. Обзор системы

**uni-hrm** -- комплексная система управления кадрами, спроектированная для высших учебных заведений Республики Узбекистан. Система охватывает полный жизненный цикл сотрудника: от найма и оформления до аттестации, расчёта зарплаты и увольнения.

### Ключевые возможности

- Управление сотрудниками (ППС, АУП, УВП, хозяйственный персонал)
- Организационная структура (факультеты, кафедры, отделы) с иерархией MPTT
- Учёт академической нагрузки и конкурсов на замещение должностей
- Управление отпусками с многоуровневым согласованием
- Табельный учёт рабочего времени
- Подбор персонала (вакансии, кандидаты, этапы интервью)
- Расчёт заработной платы с учётом узбекистанского законодательства
- Аттестация сотрудников по KPI
- Обучение и повышение квалификации
- Генерация документов (приказы, справки, договоры)
- Уведомления (in-app, email, Telegram)
- Отчётность и аналитика
- Интеграция с HEMIS (OAuth + синхронизация данных)
- Telegram-бот для OTP-аутентификации

### Целевая аудитория

| Роль | Описание |
|------|----------|
| Ректорат | Стратегическое управление, аналитика |
| Отдел кадров | Полный цикл HR-процессов |
| Деканаты | Управление персоналом факультета |
| Заведующие кафедрами | Управление персоналом кафедры |
| Бухгалтерия | Расчёт зарплаты, отчётность |
| Сотрудники | Self-service портал |

---

## 2. Структура монорепо

```
uni-hrm/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── __init__.py          # Определение текущего окружения
│   │   │   ├── base.py              # Общие настройки (INSTALLED_APPS, MIDDLEWARE, AUTH, i18n)
│   │   │   ├── development.py       # Локальная разработка (SQLite, DEBUG=True, CORS allow all)
│   │   │   └── production.py        # Production (PostgreSQL, Gunicorn, Sentry, HTTPS)
│   │   ├── urls.py                  # Корневой URL-конфигуратор
│   │   ├── wsgi.py                  # WSGI entrypoint для Gunicorn
│   │   ├── asgi.py                  # ASGI entrypoint для Django Channels (WebSocket)
│   │   └── celery.py                # Конфигурация Celery (broker, beat schedule)
│   ├── apps/
│   │   ├── core/                    # Базовые абстракции, permissions, validators, pagination
│   │   ├── accounts/                # User, Role, UserRole, OTPCode, auth backends
│   │   ├── employees/               # Employee, EmployeeCategory, EmploymentType, History
│   │   ├── departments/             # Department (MPTT), DepartmentType, Position
│   │   ├── academic/                # AcademicDegree, AcademicTitle, Subject, Load, Contest
│   │   ├── leaves/                  # LeaveType, LeaveAllocation, LeaveRequest
│   │   ├── attendance/              # WorkSchedule, AttendanceRecord, TimeSheet
│   │   ├── recruitment/             # Vacancy, Candidate, InterviewStage
│   │   ├── payroll/                 # SalaryGrade, Allowance, PayrollPeriod, PayrollEntry
│   │   ├── appraisal/              # AppraisalCycle, KPIIndicator, EmployeeAppraisal
│   │   ├── training/               # TrainingProgram, TrainingRecord
│   │   ├── documents/              # DocumentTemplate, GeneratedDocument
│   │   ├── notifications/          # NotificationTemplate, Notification
│   │   └── reports/                # Сервисный слой без моделей (ReportService)
│   ├── integrations/
│   │   ├── hemis/                   # HEMIS OAuth-клиент + data sync service
│   │   └── telegram/                # Telegram Gateway OTP + Bot webhook handlers
│   ├── locale/                      # Файлы переводов (ru, uz, en)
│   │   ├── ru/LC_MESSAGES/
│   │   ├── uz/LC_MESSAGES/
│   │   └── en/LC_MESSAGES/
│   ├── templates/                   # Email-шаблоны, шаблоны документов (Jinja2)
│   ├── media/                       # Загруженные файлы (аватары, резюме, сертификаты)
│   ├── static/                      # Статические файлы (собранные collectstatic)
│   ├── manage.py
│   └── pyproject.toml               # Python-зависимости (uv)
├── frontend/
│   ├── public/                      # Статические ассеты (favicon, manifest)
│   ├── src/
│   │   ├── app/
│   │   │   ├── router.tsx           # React Router v7 -- все маршруты приложения
│   │   │   ├── layouts/
│   │   │   │   ├── MainLayout.tsx   # Sidebar + Header + Content area
│   │   │   │   ├── AuthLayout.tsx   # Минимальный layout для login/register
│   │   │   │   └── MiniAppLayout.tsx # Layout для Telegram Mini App
│   │   │   └── providers/
│   │   │       ├── QueryClientProvider.tsx  # TanStack Query конфигурация
│   │   │       ├── AuthProvider.tsx         # Контекст аутентификации
│   │   │       ├── I18nProvider.tsx         # i18next инициализация
│   │   │       └── ThemeProvider.tsx        # Тёмная/светлая тема
│   │   ├── modules/
│   │   │   ├── auth/                # Login, ProfileCompletion, OfferAcceptance, OTP, PendingApproval
│   │   │   ├── dashboard/           # DashboardPage, StatsCards, Charts, RecentActivity
│   │   │   ├── employees/           # EmployeeList, EmployeeDetail, EmployeeForm, EmployeeCard
│   │   │   ├── departments/         # OrgChart, DepartmentTree, DepartmentDetail
│   │   │   ├── academic/            # AcademicLoadTable, ContestList, DegreeManagement
│   │   │   ├── leaves/              # LeaveBalance, LeaveRequestForm, LeaveCalendar, Management
│   │   │   ├── attendance/          # DailyAttendance, TimeSheet, AttendanceImport
│   │   │   ├── recruitment/         # VacancyList, CandidatePipeline (Kanban), VacancyDetail
│   │   │   ├── payroll/             # PayrollPeriods, PayslipView, PayrollCalculation
│   │   │   ├── reports/             # AnalyticsDashboard, ReportGenerator
│   │   │   ├── settings/            # RoleManagement, TemplateEditor, ScheduleConfig
│   │   │   └── notifications/       # NotificationCenter, NotificationPreferences
│   │   ├── shared/
│   │   │   ├── ui/                  # shadcn/ui компоненты (Button, Input, Table, Modal, Badge)
│   │   │   ├── hooks/               # useAuth, usePermission, usePagination, useDebounce
│   │   │   ├── utils/               # formatDate, formatCurrency, cn(), validators
│   │   │   ├── api/                 # axios instance, interceptors, apiClient
│   │   │   └── types/               # Общие TypeScript-интерфейсы
│   │   ├── i18n/
│   │   │   ├── config.ts            # i18next инициализация
│   │   │   ├── ru.json              # Русский
│   │   │   ├── uz.json              # Узбекский
│   │   │   └── en.json              # Английский
│   │   └── store/
│   │       ├── authStore.ts         # User, tokens, permissions (Zustand)
│   │       ├── uiStore.ts           # Sidebar, theme, locale (Zustand)
│   │       └── notificationStore.ts # Уведомления (Zustand)
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
├── docker/
│   ├── backend/Dockerfile           # Python 3.12, uv, multi-stage build
│   ├── frontend/Dockerfile          # Node 22, npm, multi-stage build
│   └── nginx/
│       ├── Dockerfile               # Nginx Alpine
│       └── nginx.conf               # Reverse proxy + static serving
├── docker-compose.yml               # Development (all services)
├── docker-compose.prod.yml          # Production (с volumes, restart policies)
└── .github/
    └── workflows/
        ├── ci.yml                   # Lint + Test on PR (ruff, pytest, biome, vitest)
        └── deploy.yml               # Build + Deploy on merge to main
```

### Описание приложений (apps)

| Приложение | Назначение | Модели |
|------------|-----------|--------|
| `core` | Базовые абстракции, общие компоненты | TimestampedModel, SoftDeleteModel (абстрактные) |
| `accounts` | Аутентификация, авторизация, роли | User, Role, UserRole, OTPCode |
| `employees` | Управление сотрудниками | Employee, EmployeeCategory, EmploymentType, EmploymentHistory |
| `departments` | Организационная структура | Department, DepartmentType, Position |
| `academic` | Академическая деятельность | AcademicDegree, AcademicTitle, EmployeeAcademicInfo, Subject, AcademicLoad, PositionContest, ContestApplication |
| `leaves` | Управление отпусками | LeaveType, LeaveAllocation, LeaveRequest |
| `attendance` | Табельный учёт | WorkSchedule, AttendanceRecord, TimeSheet |
| `recruitment` | Подбор персонала | Vacancy, Candidate, InterviewStage |
| `payroll` | Расчёт зарплаты | SalaryGrade, Allowance, EmployeeAllowance, PayrollPeriod, PayrollEntry |
| `appraisal` | Аттестация | AppraisalCycle, KPIIndicator, EmployeeAppraisal |
| `training` | Обучение | TrainingProgram, TrainingRecord |
| `documents` | Генерация документов | DocumentTemplate, GeneratedDocument |
| `notifications` | Уведомления | NotificationTemplate, Notification |
| `reports` | Отчётность | Без моделей, сервисный слой |

---

## 3. Backend-архитектура

### Технологический стек

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Язык | Python | 3.12+ |
| Фреймворк | Django | 5.1+ |
| API | Django REST Framework | 3.15+ |
| Admin | Django Unfold | 0.40+ |
| Task Queue | Celery | 5.4+ |
| Broker | Redis | 7+ |
| WebSocket | Django Channels | 4+ |
| Деревья | django-mptt | 0.16+ |
| JWT | djangorestframework-simplejwt | 5.3+ |
| CORS | django-cors-headers | 4+ |
| Фильтрация | django-filter | 24+ |
| i18n | Django built-in + gettext | -- |
| Package Manager | uv | latest |

### Слоистая архитектура

```
┌─────────────────────────────────────────────────────┐
│                    API Layer                         │
│  (ViewSets, APIViews, Serializers, Permissions)      │
├─────────────────────────────────────────────────────┤
│                  Service Layer                       │
│  (Business logic, Calculations, External APIs)       │
├─────────────────────────────────────────────────────┤
│                   Model Layer                        │
│  (Django ORM, Managers, QuerySets, Validators)       │
├─────────────────────────────────────────────────────┤
│                Infrastructure Layer                  │
│  (Celery Tasks, Cache, File Storage, Email)          │
└─────────────────────────────────────────────────────┘
```

**Принципы:**

1. **ViewSets** отвечают только за HTTP-взаимодействие: приём запроса, валидация через serializer, вызов service, формирование ответа.
2. **Services** содержат бизнес-логику: расчёт зарплаты, workflow отпусков, генерация документов. Не зависят от HTTP.
3. **Models** определяют структуру данных, валидацию на уровне полей, QuerySet-менеджеры для частых запросов.
4. **Tasks** (Celery) -- асинхронные операции: отправка уведомлений, генерация отчётов, синхронизация с HEMIS.

### Структура приложения (каждый app)

```
apps/employees/
├── __init__.py
├── admin.py              # Unfold Admin конфигурация
├── apps.py               # AppConfig
├── models.py             # Django модели
├── serializers.py        # DRF сериализаторы
├── views.py              # ViewSets и APIViews
├── urls.py               # URL-маршруты приложения
├── permissions.py         # Кастомные permissions
├── filters.py            # django-filter фильтры
├── services.py           # Бизнес-логика
├── signals.py            # Django signals (post_save, etc.)
├── tasks.py              # Celery tasks
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_serializers.py
│   ├── test_views.py
│   └── test_services.py
└── migrations/
    └── __init__.py
```

### Настройки (settings)

**base.py** -- общие настройки:
- `INSTALLED_APPS`: все Django-приложения + third-party
- `MIDDLEWARE`: security, session, auth, CORS, locale
- `AUTH_USER_MODEL = "accounts.User"`
- `REST_FRAMEWORK`: default authentication (JWT), permission (IsAuthenticated), pagination (CursorPagination), versioning (URLPathVersioning), throttle rates
- `SIMPLE_JWT`: access token lifetime (15 min), refresh (7 days), rotate refresh tokens
- `CELERY_*`: broker URL, result backend, task serializer, beat schedule
- `LANGUAGES`: ru, uz, en
- `LOCALE_PATHS`: путь к файлам переводов

**development.py** -- разработка:
- `DEBUG = True`
- `DATABASES`: SQLite
- `CORS_ALLOW_ALL_ORIGINS = True`
- `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"`

**production.py** -- продакшн:
- `DEBUG = False`
- `DATABASES`: PostgreSQL (из `DATABASE_URL`)
- `CORS_ALLOWED_ORIGINS`: whitelist
- `SECURE_SSL_REDIRECT = True`
- `CACHES`: Redis
- `STATIC_ROOT`, `MEDIA_ROOT`
- Sentry DSN для мониторинга ошибок

---

## 4. Frontend-архитектура

### Технологический стек

| Компонент | Технология | Версия |
|-----------|-----------|--------|
| Язык | TypeScript | 5.6+ |
| Фреймворк | React | 19 |
| Сборщик | Vite | 6+ |
| Стили | Tailwind CSS | 4+ |
| UI Kit | shadcn/ui | latest |
| State Management | Zustand | 5+ |
| Server State | TanStack Query | 5+ |
| Роутинг | React Router | 7 |
| HTTP Client | Axios | 1.7+ |
| Формы | React Hook Form + Zod | -- |
| i18n | i18next + react-i18next | -- |
| Графики | Recharts | 2+ |

### Модульная архитектура

```
src/
├── app/           # Инициализация, роутинг, провайдеры
├── modules/       # Feature modules (domain-driven)
├── shared/        # Переиспользуемые компоненты, хуки, утилиты
├── store/         # Глобальное состояние (Zustand)
└── i18n/          # Локализация
```

**Принцип:** каждый модуль (`modules/*`) -- самостоятельная фича со своими страницами, компонентами, хуками и типами. Модули не импортируют друг из друга напрямую -- общий код выносится в `shared/`.

### Роутинг

```tsx
// app/router.tsx -- верхнеуровневая структура маршрутов

/login                          → AuthLayout > LoginPage
/profile/complete               → AuthLayout > ProfileCompletion
/offer/accept                   → AuthLayout > OfferAcceptance
/pending-approval               → AuthLayout > PendingApproval

/                               → MainLayout > DashboardPage
/employees                      → MainLayout > EmployeeList
/employees/:id                  → MainLayout > EmployeeDetail
/employees/new                  → MainLayout > EmployeeForm
/departments                    → MainLayout > DepartmentTree
/departments/:id                → MainLayout > DepartmentDetail
/org-chart                      → MainLayout > OrgChart
/academic/load                  → MainLayout > AcademicLoadTable
/academic/contests              → MainLayout > ContestList
/leaves                         → MainLayout > LeaveManagement
/leaves/calendar                → MainLayout > LeaveCalendar
/attendance                     → MainLayout > DailyAttendance
/attendance/timesheet           → MainLayout > TimeSheet
/recruitment                    → MainLayout > VacancyList
/recruitment/:id                → MainLayout > VacancyDetail
/recruitment/:id/pipeline       → MainLayout > CandidatePipeline
/payroll                        → MainLayout > PayrollPeriods
/payroll/:periodId/payslip/:id  → MainLayout > PayslipView
/reports                        → MainLayout > AnalyticsDashboard
/settings                       → MainLayout > Settings
/settings/roles                 → MainLayout > RoleManagement
/notifications                  → MainLayout > NotificationCenter
```

### Управление состоянием

| Store | Содержимое | Persistence |
|-------|-----------|-------------|
| `authStore` | User, accessToken, refreshToken, permissions, roles | localStorage (tokens) |
| `uiStore` | sidebarCollapsed, theme (light/dark), locale (ru/uz/en) | localStorage |
| `notificationStore` | unreadCount, notifications[] | -- |

**TanStack Query** используется для серверного состояния (списки сотрудников, отпуска и т.д.) с автоматическим кешированием, refetch и optimistic updates.

### Паттерн API-вызовов

```tsx
// shared/api/apiClient.ts
const apiClient = axios.create({
  baseURL: "/api/v1/",
  headers: { "Content-Type": "application/json" },
});

// Request interceptor: добавляет Authorization header
// Response interceptor: обрабатывает 401 → refresh token → retry
```

```tsx
// modules/employees/hooks/useEmployees.ts
export function useEmployees(params: EmployeeListParams) {
  return useQuery({
    queryKey: ["employees", params],
    queryFn: () => apiClient.get<PaginatedResponse<Employee>>("/employees/", { params }),
  });
}
```

---

## 5. RBAC-модель

### Роли

Система использует 8 предустановленных ролей с тремя уровнями доступа.

| # | Роль | Код | Уровень | Описание |
|---|------|-----|---------|----------|
| 1 | Super Admin | `super_admin` | Global | Полный доступ ко всей системе, управление настройками |
| 2 | Admin | `admin` | Global | Управление пользователями, ролями, настройками |
| 3 | HR Manager | `hr_manager` | Global | Полный цикл HR: сотрудники, отпуска, найм, зарплата |
| 4 | Dean | `dean` | Department | Управление сотрудниками своего факультета |
| 5 | Head of Department | `head_of_department` | Department | Управление сотрудниками своей кафедры, одобрение отпусков |
| 6 | Accountant | `accountant` | Global | Доступ к зарплате, финансовым отчётам |
| 7 | Employee | `employee` | Personal | Self-service: свой профиль, отпуска, расчётные листки |
| 8 | External | `external` | Personal | Ограниченный доступ (совместители, почасовики) |

### Уровни доступа (Permission Levels)

| Уровень | Описание | Пример |
|---------|----------|--------|
| **Global** | Доступ ко всем данным системы | HR Manager видит всех сотрудников |
| **Department** | Доступ к данным своего подразделения (факультет/кафедра) | Dean видит только сотрудников своего факультета |
| **Personal** | Доступ только к собственным данным | Employee видит только свой профиль |

### Матрица разрешений

Обозначения: **C** = Create, **R** = Read, **U** = Update, **D** = Delete, **-** = нет доступа, **(own)** = только свои данные, **(dept)** = только данные своего подразделения.

| Модуль | Super Admin | Admin | HR Manager | Dean | Head of Dept | Accountant | Employee | External |
|--------|------------|-------|------------|------|-------------|------------|----------|----------|
| **Пользователи** | CRUD | CRUD | CRU | R(dept) | R(dept) | - | R(own) | R(own) |
| **Роли** | CRUD | CRU | R | - | - | - | - | - |
| **Сотрудники** | CRUD | CRUD | CRUD | RU(dept) | R(dept) | R | R(own) | R(own) |
| **Подразделения** | CRUD | CRUD | CRU | RU(dept) | R(dept) | R | R | R |
| **Должности** | CRUD | CRUD | CRU | R | R | R | R | - |
| **Академическая информация** | CRUD | CRUD | CRUD | RU(dept) | RU(dept) | - | RU(own) | R(own) |
| **Учебная нагрузка** | CRUD | CRUD | CRUD | CRUD(dept) | CRUD(dept) | - | R(own) | R(own) |
| **Конкурсы** | CRUD | CRUD | CRUD | CRUD(dept) | R(dept) | - | R | R |
| **Типы отпусков** | CRUD | CRUD | CRU | R | R | - | R | R |
| **Заявки на отпуск** | CRUD | CRUD | CRUD | RU(dept) | RU(dept) | - | CRU(own) | CR(own) |
| **Табель** | CRUD | CRUD | CRUD | RU(dept) | RU(dept) | R | R(own) | R(own) |
| **Вакансии** | CRUD | CRUD | CRUD | CR(dept) | R(dept) | - | R | - |
| **Кандидаты** | CRUD | CRUD | CRUD | R(dept) | R(dept) | - | - | - |
| **Зарплата (грейды)** | CRUD | CRU | CRU | R | R | RU | - | - |
| **Расчёт зарплаты** | CRUD | R | CRUD | - | - | CRUD | R(own) | R(own) |
| **Аттестация** | CRUD | CRUD | CRUD | CRUD(dept) | CRUD(dept) | - | RU(own) | - |
| **Обучение** | CRUD | CRUD | CRUD | CRU(dept) | R(dept) | - | R(own) | - |
| **Шаблоны документов** | CRUD | CRUD | CRU | R | R | R | - | - |
| **Генерация документов** | CRUD | CRUD | CRUD | CR(dept) | R(dept) | R | R(own) | - |
| **Уведомления** | CRUD | CRUD | CRUD | R(own) | R(own) | R(own) | R(own) | R(own) |
| **Отчёты** | CRUD | RU | CRUD | R(dept) | R(dept) | R | - | - |
| **Настройки системы** | CRUD | RU | R | - | - | - | - | - |

### Реализация RBAC

```python
# apps/core/permissions.py

class RoleBasedPermission(permissions.BasePermission):
    """
    Базовый permission-класс для RBAC.
    Проверяет роль пользователя и уровень доступа.
    """

    required_roles: list[str] = []

    def has_permission(self, request, view) -> bool:
        if not request.user.is_authenticated:
            return False
        user_roles = request.user.get_role_codes()
        return bool(set(self.required_roles) & set(user_roles))

    def has_object_permission(self, request, view, obj) -> bool:
        user_roles = request.user.user_roles.select_related("role", "department")
        for user_role in user_roles:
            if user_role.role.level == "global":
                return True
            if user_role.role.level == "department":
                return self._check_department_access(user_role, obj)
            if user_role.role.level == "personal":
                return self._check_personal_access(request.user, obj)
        return False
```

### Workflow согласования отпуска

```
Employee создаёт LeaveRequest (status: draft)
    │
    ▼
Employee отправляет на согласование (status: pending_head)
    │
    ▼
Head of Department / Dean одобряет (status: pending_hr)
    │                      │
    │                  отклоняет → (status: rejected)
    ▼
HR Manager одобряет (status: approved)
    │                 │
    │             отклоняет → (status: rejected)
    ▼
Уведомление сотруднику + обновление LeaveAllocation
```

---

## 6. API Versioning

### Стратегия версионирования

| Параметр | Значение |
|----------|---------|
| Тип | URL Path Versioning |
| Префикс | `/api/v1/` |
| DRF класс | `rest_framework.versioning.URLPathVersioning` |
| Текущая версия | `v1` |

### Настройка

```python
# config/settings/base.py
REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "VERSION_PARAM": "version",
}
```

### URL-структура

```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("config.api_v1_urls")),
    # Будущие версии:
    # path("api/v2/", include("config.api_v2_urls")),
]
```

### Основные API-эндпоинты (v1)

```
# Аутентификация
POST   /api/v1/auth/login/                    # JWT login
POST   /api/v1/auth/refresh/                  # Refresh token
POST   /api/v1/auth/otp/request/              # Запросить OTP
POST   /api/v1/auth/otp/verify/               # Подтвердить OTP
POST   /api/v1/auth/logout/                   # Logout (blacklist token)
GET    /api/v1/auth/me/                        # Текущий пользователь

# Сотрудники
GET    /api/v1/employees/                      # Список сотрудников (с фильтрацией)
POST   /api/v1/employees/                      # Создать сотрудника
GET    /api/v1/employees/{id}/                 # Детали сотрудника
PATCH  /api/v1/employees/{id}/                 # Обновить сотрудника
DELETE /api/v1/employees/{id}/                 # Soft-delete сотрудника
GET    /api/v1/employees/{id}/history/         # История должностей
GET    /api/v1/employees/{id}/academic/        # Академическая информация
GET    /api/v1/employees/{id}/leaves/          # Отпуска сотрудника
GET    /api/v1/employees/{id}/payslips/        # Расчётные листки

# Подразделения
GET    /api/v1/departments/                    # Список (дерево)
POST   /api/v1/departments/                    # Создать подразделение
GET    /api/v1/departments/{id}/               # Детали
PATCH  /api/v1/departments/{id}/               # Обновить
GET    /api/v1/departments/{id}/employees/     # Сотрудники подразделения
GET    /api/v1/departments/{id}/children/      # Дочерние подразделения
GET    /api/v1/departments/tree/               # Полное дерево

# Отпуска
GET    /api/v1/leaves/types/                   # Типы отпусков
GET    /api/v1/leaves/allocations/             # Балансы отпусков
GET    /api/v1/leaves/requests/                # Заявки на отпуск
POST   /api/v1/leaves/requests/                # Создать заявку
PATCH  /api/v1/leaves/requests/{id}/           # Обновить заявку
POST   /api/v1/leaves/requests/{id}/approve/   # Одобрить
POST   /api/v1/leaves/requests/{id}/reject/    # Отклонить
GET    /api/v1/leaves/calendar/                # Календарь отпусков

# Табель
GET    /api/v1/attendance/records/             # Записи посещаемости
POST   /api/v1/attendance/records/             # Создать запись
POST   /api/v1/attendance/import/              # Импорт из биометрии
GET    /api/v1/attendance/timesheets/          # Табели
PATCH  /api/v1/attendance/timesheets/{id}/approve/ # Утвердить табель

# Рекрутинг
GET    /api/v1/recruitment/vacancies/          # Вакансии
POST   /api/v1/recruitment/vacancies/          # Создать вакансию
GET    /api/v1/recruitment/candidates/         # Кандидаты
POST   /api/v1/recruitment/candidates/         # Создать кандидата
PATCH  /api/v1/recruitment/candidates/{id}/stage/ # Обновить этап

# Зарплата
GET    /api/v1/payroll/periods/                # Периоды расчёта
POST   /api/v1/payroll/periods/{id}/calculate/ # Запустить расчёт
POST   /api/v1/payroll/periods/{id}/approve/   # Утвердить
GET    /api/v1/payroll/entries/                # Записи расчёта

# Академическая деятельность
GET    /api/v1/academic/subjects/              # Предметы
GET    /api/v1/academic/load/                  # Нагрузка
GET    /api/v1/academic/contests/              # Конкурсы
POST   /api/v1/academic/contests/{id}/apply/   # Подать заявку

# Документы
GET    /api/v1/documents/templates/            # Шаблоны
POST   /api/v1/documents/generate/             # Сгенерировать документ

# Отчёты
GET    /api/v1/reports/summary/                # Сводка по организации
GET    /api/v1/reports/employees/              # Отчёт по сотрудникам
GET    /api/v1/reports/leaves/                 # Отчёт по отпускам
GET    /api/v1/reports/payroll/                # Отчёт по зарплате
GET    /api/v1/reports/attendance/             # Отчёт по посещаемости
POST   /api/v1/reports/export/                 # Экспорт в Excel/PDF

# Уведомления
GET    /api/v1/notifications/                  # Список уведомлений
PATCH  /api/v1/notifications/{id}/read/        # Отметить как прочитанное
POST   /api/v1/notifications/read-all/         # Отметить все как прочитанные
```

### Правила версионирования

1. **Обратная совместимость** -- изменения, не ломающие клиента (добавление полей, новых endpoints), делаются в текущей версии.
2. **Breaking changes** -- удаление полей, изменение типов, изменение поведения -- требуют новой версии API.
3. **Deprecation policy** -- старая версия поддерживается минимум 6 месяцев после выхода новой.
4. **Header `Sunset`** -- при deprecation API возвращает заголовок `Sunset` с датой окончания поддержки.

---

## 7. ERD-диаграмма

```mermaid
erDiagram
    %% ============================
    %% ACCOUNTS
    %% ============================
    User {
        uuid id PK
        string email UK
        string password
        string first_name
        string last_name
        string middle_name
        string phone
        string avatar
        string language
        bigint telegram_id
        string telegram_username
        boolean is_profile_completed
        boolean is_offer_accepted
        boolean is_approved
        uuid approved_by FK
        datetime approved_at
        datetime date_joined
        boolean is_active
        boolean is_staff
        boolean is_superuser
    }

    Role {
        uuid id PK
        string name
        string code UK
        string description
        string level
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    UserRole {
        uuid id PK
        uuid user_id FK
        uuid role_id FK
        uuid department_id FK
        uuid assigned_by FK
        datetime assigned_at
        datetime created_at
        datetime updated_at
    }

    OTPCode {
        uuid id PK
        uuid user_id FK
        string code
        string channel
        datetime created_at
        datetime expires_at
        boolean is_used
        integer attempts
    }

    %% ============================
    %% DEPARTMENTS
    %% ============================
    DepartmentType {
        uuid id PK
        json name
        string code UK
        datetime created_at
        datetime updated_at
    }

    Department {
        uuid id PK
        json name
        string code UK
        uuid department_type_id FK
        uuid parent_id FK
        uuid head_id FK
        string email
        string phone
        date established_date
        boolean is_active
        integer order
        integer lft
        integer rght
        integer tree_id
        integer level
        datetime created_at
        datetime updated_at
    }

    Position {
        uuid id PK
        json name
        string code UK
        uuid department_type_id FK
        string category
        decimal min_salary
        decimal max_salary
        text requirements
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    %% ============================
    %% EMPLOYEES
    %% ============================
    EmployeeCategory {
        uuid id PK
        string name
        string code UK
        string description
        datetime created_at
        datetime updated_at
    }

    EmploymentType {
        uuid id PK
        string name
        string code UK
        datetime created_at
        datetime updated_at
    }

    Employee {
        uuid id PK
        uuid user_id FK
        string employee_number UK
        uuid department_id FK
        uuid position_id FK
        uuid category_id FK
        uuid employment_type_id FK
        date date_of_birth
        string gender
        string nationality
        string pinfl
        string inn
        string passport_series
        string passport_number
        string passport_issued_by
        date passport_issued_date
        date passport_expires_date
        text registration_address
        text actual_address
        string emergency_contact_name
        string emergency_contact_phone
        date hire_date
        date probation_end_date
        date contract_end_date
        date termination_date
        text termination_reason
        string status
        string photo
        text notes
        boolean is_deleted
        datetime deleted_at
        datetime created_at
        datetime updated_at
    }

    EmploymentHistory {
        uuid id PK
        uuid employee_id FK
        uuid department_id FK
        uuid position_id FK
        uuid employment_type_id FK
        date start_date
        date end_date
        string order_number
        date order_date
        string reason
        text notes
        datetime created_at
        datetime updated_at
    }

    %% ============================
    %% ACADEMIC
    %% ============================
    AcademicDegree {
        uuid id PK
        json name
        string code UK
        text description
        datetime created_at
        datetime updated_at
    }

    AcademicTitle {
        uuid id PK
        json name
        string code UK
        text description
        datetime created_at
        datetime updated_at
    }

    EmployeeAcademicInfo {
        uuid id PK
        uuid employee_id FK
        uuid degree_id FK
        string degree_specialty
        date degree_date
        string degree_certificate_number
        uuid title_id FK
        date title_date
        string title_certificate_number
        integer h_index
        string scopus_id
        string orcid_id
        string google_scholar_id
        integer publications_count
        text scientific_interests
        datetime created_at
        datetime updated_at
    }

    Subject {
        uuid id PK
        json name
        string code UK
        uuid department_id FK
        integer credits
        integer hours_lecture
        integer hours_practice
        integer hours_lab
        integer hours_total
        integer semester
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    AcademicLoad {
        uuid id PK
        uuid employee_id FK
        uuid subject_id FK
        string academic_year
        integer semester
        integer hours_planned
        integer hours_actual
        integer groups_count
        integer students_count
        string load_type
        text notes
        datetime created_at
        datetime updated_at
    }

    PositionContest {
        uuid id PK
        uuid position_id FK
        uuid department_id FK
        string academic_year
        date announcement_date
        date application_deadline
        date review_date
        date decision_date
        string status
        uuid required_degree_id FK
        uuid required_title_id FK
        integer min_experience_years
        text description
        uuid winner_id FK
        string protocol_number
        datetime created_at
        datetime updated_at
    }

    ContestApplication {
        uuid id PK
        uuid contest_id FK
        uuid employee_id FK
        string candidate_name
        string candidate_email
        string candidate_phone
        json documents
        datetime submitted_at
        string status
        uuid reviewer_id FK
        text review_notes
        datetime reviewed_at
        datetime created_at
        datetime updated_at
    }

    %% ============================
    %% LEAVES
    %% ============================
    LeaveType {
        uuid id PK
        json name
        string code UK
        integer days_per_year
        boolean is_paid
        boolean requires_document
        integer max_consecutive_days
        text description
        datetime created_at
        datetime updated_at
    }

    LeaveAllocation {
        uuid id PK
        uuid employee_id FK
        uuid leave_type_id FK
        integer year
        integer total_days
        integer used_days
        integer remaining_days
        integer carried_over_days
        date expires_at
        datetime created_at
        datetime updated_at
    }

    LeaveRequest {
        uuid id PK
        uuid employee_id FK
        uuid leave_type_id FK
        date start_date
        date end_date
        integer total_days
        text reason
        string supporting_document
        string status
        uuid head_approved_by FK
        datetime head_approved_at
        text head_comment
        uuid hr_approved_by FK
        datetime hr_approved_at
        text hr_comment
        datetime created_at
        datetime updated_at
    }

    %% ============================
    %% ATTENDANCE
    %% ============================
    WorkSchedule {
        uuid id PK
        string name
        string code UK
        time start_time
        time end_time
        time break_start
        time break_end
        json working_days
        boolean is_default
        datetime created_at
        datetime updated_at
    }

    AttendanceRecord {
        uuid id PK
        uuid employee_id FK
        date date
        time check_in
        time check_out
        string status
        uuid work_schedule_id FK
        decimal actual_hours
        decimal overtime_hours
        text notes
        string source
        datetime created_at
        datetime updated_at
    }

    TimeSheet {
        uuid id PK
        uuid employee_id FK
        integer year
        integer month
        integer total_working_days
        integer days_present
        integer days_absent
        integer days_late
        integer days_on_leave
        integer days_holiday
        decimal total_hours
        decimal overtime_hours
        string status
        uuid approved_by FK
        datetime approved_at
        datetime created_at
        datetime updated_at
    }

    %% ============================
    %% RECRUITMENT
    %% ============================
    Vacancy {
        uuid id PK
        uuid position_id FK
        uuid department_id FK
        string title
        text description
        text requirements
        decimal salary_min
        decimal salary_max
        uuid employment_type_id FK
        integer openings_count
        datetime published_at
        date deadline
        string status
        uuid created_by FK
        datetime created_at
        datetime updated_at
    }

    Candidate {
        uuid id PK
        uuid vacancy_id FK
        string first_name
        string last_name
        string middle_name
        string email
        string phone
        string resume
        text cover_letter
        string source
        string status
        datetime applied_at
        text notes
        datetime created_at
        datetime updated_at
    }

    InterviewStage {
        uuid id PK
        uuid candidate_id FK
        string stage_name
        uuid interviewer_id FK
        datetime scheduled_at
        datetime completed_at
        integer score
        text feedback
        string result
        datetime created_at
        datetime updated_at
    }

    %% ============================
    %% PAYROLL
    %% ============================
    SalaryGrade {
        uuid id PK
        string name
        string code UK
        decimal base_salary
        string currency
        date effective_from
        date effective_to
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    Allowance {
        uuid id PK
        string name
        string code UK
        string type
        decimal amount
        decimal percentage
        text description
        boolean is_taxable
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    EmployeeAllowance {
        uuid id PK
        uuid employee_id FK
        uuid allowance_id FK
        decimal custom_amount
        date start_date
        date end_date
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    PayrollPeriod {
        uuid id PK
        integer year
        integer month
        date start_date
        date end_date
        string status
        uuid calculated_by FK
        datetime calculated_at
        uuid approved_by FK
        datetime approved_at
        decimal total_gross
        decimal total_net
        decimal total_tax
        decimal total_deductions
        datetime created_at
        datetime updated_at
    }

    PayrollEntry {
        uuid id PK
        uuid payroll_period_id FK
        uuid employee_id FK
        decimal base_salary
        decimal total_allowances
        decimal gross_salary
        decimal income_tax
        decimal pension_contribution
        decimal other_deductions
        decimal net_salary
        integer working_days
        integer actual_days
        decimal overtime_hours
        decimal overtime_amount
        integer sick_leave_days
        decimal sick_leave_amount
        text notes
        json details
        datetime created_at
        datetime updated_at
    }

    %% ============================
    %% APPRAISAL
    %% ============================
    AppraisalCycle {
        uuid id PK
        string name
        integer year
        date start_date
        date end_date
        string status
        datetime created_at
        datetime updated_at
    }

    KPIIndicator {
        uuid id PK
        string name
        string code UK
        text description
        decimal weight
        decimal target_value
        string unit
        string category
        datetime created_at
        datetime updated_at
    }

    EmployeeAppraisal {
        uuid id PK
        uuid cycle_id FK
        uuid employee_id FK
        uuid reviewer_id FK
        string status
        decimal self_score
        decimal manager_score
        decimal final_score
        text self_comments
        text manager_comments
        text goals_next_period
        datetime reviewed_at
        datetime created_at
        datetime updated_at
    }

    %% ============================
    %% TRAINING
    %% ============================
    TrainingProgram {
        uuid id PK
        string name
        text description
        string provider
        string type
        date start_date
        date end_date
        integer hours
        integer max_participants
        decimal cost_per_person
        boolean is_mandatory
        datetime created_at
        datetime updated_at
    }

    TrainingRecord {
        uuid id PK
        uuid employee_id FK
        uuid program_id FK
        string status
        datetime enrolled_at
        datetime completed_at
        string certificate_number
        string certificate_file
        decimal score
        text feedback
        datetime created_at
        datetime updated_at
    }

    %% ============================
    %% DOCUMENTS
    %% ============================
    DocumentTemplate {
        uuid id PK
        string name
        string code UK
        string template_file
        text description
        boolean is_active
        datetime created_at
        datetime updated_at
    }

    GeneratedDocument {
        uuid id PK
        uuid template_id FK
        uuid employee_id FK
        uuid generated_by FK
        string document_number
        datetime generated_at
        string file
        json parameters
        string status
        datetime created_at
        datetime updated_at
    }

    %% ============================
    %% NOTIFICATIONS
    %% ============================
    NotificationTemplate {
        uuid id PK
        string name
        string code UK
        string subject_template
        text body_template
        json channels
        string event_type
        datetime created_at
        datetime updated_at
    }

    Notification {
        uuid id PK
        uuid recipient_id FK
        uuid template_id FK
        string title
        text message
        string channel
        boolean is_read
        datetime read_at
        json data
        datetime created_at
    }

    %% ============================
    %% RELATIONSHIPS
    %% ============================

    User ||--o| Employee : "has profile"
    User ||--o{ UserRole : "has roles"
    User ||--o{ OTPCode : "has OTP codes"
    User ||--o{ Notification : "receives"

    Role ||--o{ UserRole : "assigned to"
    UserRole }o--o| Department : "scoped to"

    DepartmentType ||--o{ Department : "categorizes"
    DepartmentType ||--o{ Position : "applicable to"
    Department ||--o{ Department : "parent-children (MPTT)"
    Department ||--o{ Employee : "employs"
    Department ||--o{ Subject : "teaches"
    Department ||--o{ Vacancy : "has openings"
    Department ||--o{ PositionContest : "holds contests"
    Department |o--o| Employee : "headed by"

    Position ||--o{ Employee : "holds"
    Position ||--o{ Vacancy : "opens"
    Position ||--o{ PositionContest : "contests for"

    EmployeeCategory ||--o{ Employee : "categorizes"
    EmploymentType ||--o{ Employee : "type of"
    EmploymentType ||--o{ EmploymentHistory : "type in history"
    EmploymentType ||--o{ Vacancy : "type for vacancy"

    Employee ||--o{ EmploymentHistory : "career history"
    Employee ||--o| EmployeeAcademicInfo : "academic info"
    Employee ||--o{ AcademicLoad : "teaches"
    Employee ||--o{ LeaveAllocation : "leave balance"
    Employee ||--o{ LeaveRequest : "requests leave"
    Employee ||--o{ AttendanceRecord : "attendance"
    Employee ||--o{ TimeSheet : "timesheets"
    Employee ||--o{ EmployeeAllowance : "allowances"
    Employee ||--o{ PayrollEntry : "payroll"
    Employee ||--o{ EmployeeAppraisal : "appraised"
    Employee ||--o{ TrainingRecord : "training"
    Employee ||--o{ GeneratedDocument : "documents"
    Employee ||--o{ ContestApplication : "applies to contest"

    AcademicDegree ||--o{ EmployeeAcademicInfo : "degree held"
    AcademicDegree ||--o{ PositionContest : "required degree"
    AcademicTitle ||--o{ EmployeeAcademicInfo : "title held"
    AcademicTitle ||--o{ PositionContest : "required title"

    Subject ||--o{ AcademicLoad : "load for"

    PositionContest ||--o{ ContestApplication : "applications"
    PositionContest }o--o| Employee : "winner"

    LeaveType ||--o{ LeaveAllocation : "allocation for"
    LeaveType ||--o{ LeaveRequest : "request for"

    WorkSchedule ||--o{ AttendanceRecord : "schedule"

    Allowance ||--o{ EmployeeAllowance : "assigned"

    PayrollPeriod ||--o{ PayrollEntry : "entries"

    AppraisalCycle ||--o{ EmployeeAppraisal : "appraisals"
    KPIIndicator }o--o{ EmployeeAppraisal : "evaluated by"

    TrainingProgram ||--o{ TrainingRecord : "enrollments"
    TrainingProgram }o--o{ EmployeeCategory : "target categories (M2M)"

    DocumentTemplate ||--o{ GeneratedDocument : "generates"
    NotificationTemplate ||--o{ Notification : "based on"

    Vacancy ||--o{ Candidate : "applicants"
    Candidate ||--o{ InterviewStage : "interviews"
```

---

## 8. Deployment-архитектура

### Development (локальная разработка)

```
┌─────────────┐     ┌─────────────┐
│  Vite Dev   │     │  Django Dev │
│  Server     │────▶│  Server     │
│  :3000      │     │  :8000      │
└─────────────┘     └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   SQLite    │
                    │   db.sqlite3│
                    └─────────────┘
```

**Запуск:**
```bash
# Backend
cd backend
uv run manage.py runserver 0.0.0.0:8000

# Frontend
cd frontend
npm run dev
```

- Vite проксирует `/api/` запросы на Django (`vite.config.ts → proxy`)
- SQLite для простоты, без внешних зависимостей
- Hot Module Replacement (Vite) + Django auto-reload
- `DEBUG = True`, подробные ошибки
- Email в консоль

### Production

```
                    ┌────────────────────────────────────────────────────┐
                    │                    Docker Host                     │
                    │                                                    │
┌──────────┐       │  ┌──────────┐     ┌──────────────┐                │
│  Client  │──────▶│  │  Nginx   │────▶│  Gunicorn    │                │
│ (Browser)│  HTTPS│  │  :443    │     │  (Django)    │                │
│          │◀──────│  │  :80→443 │     │  :8000       │                │
└──────────┘       │  │          │     └──────┬───────┘                │
                    │  │  static/ │            │                        │
                    │  │  media/  │     ┌──────▼───────┐                │
                    │  └──────────┘     │  PostgreSQL  │                │
                    │                    │  :5432       │                │
                    │  ┌──────────┐     └──────────────┘                │
                    │  │  Redis   │                                     │
                    │  │  :6379   │◀───┐                                │
                    │  └──────────┘    │                                │
                    │                   │                                │
                    │  ┌──────────────┐│  ┌──────────────┐             │
                    │  │ Celery Worker├┘  │ Celery Beat  │             │
                    │  │ (async tasks)│   │ (scheduler)  │             │
                    │  └──────────────┘   └──────────────┘             │
                    │                                                    │
                    └────────────────────────────────────────────────────┘
```

### Docker Compose (Production)

```yaml
# docker-compose.prod.yml
services:
  nginx:
    build: ./docker/nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_files:/app/static
      - media_files:/app/media
      - ./docker/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
    restart: always

  backend:
    build: ./docker/backend
    env_file: .env.prod
    volumes:
      - static_files:/app/static
      - media_files:/app/media
    depends_on:
      - db
      - redis
    restart: always
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --threads 2

  celery_worker:
    build: ./docker/backend
    env_file: .env.prod
    depends_on:
      - db
      - redis
    restart: always
    command: celery -A config worker -l info --concurrency=4

  celery_beat:
    build: ./docker/backend
    env_file: .env.prod
    depends_on:
      - db
      - redis
    restart: always
    command: celery -A config beat -l info

  db:
    image: postgres:16-alpine
    env_file: .env.prod
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always

volumes:
  static_files:
  media_files:
  postgres_data:
  redis_data:
```

### Nginx-конфигурация

```nginx
# docker/nginx/nginx.conf
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name uni-hrm.example.uz;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name uni-hrm.example.uz;

    ssl_certificate     /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    client_max_body_size 20M;

    # Frontend (SPA)
    location / {
        root /app/static/frontend;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static files
    location /static/ {
        alias /app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /app/media/;
        expires 7d;
    }
}
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  backend-lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: cd backend && uv sync
      - run: cd backend && uv run ruff check .
      - run: cd backend && uv run pytest --cov=apps --cov-report=xml

  frontend-lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
      - run: cd frontend && npm ci
      - run: cd frontend && npm run lint
      - run: cd frontend && npm run build
      - run: cd frontend && npm test
```

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and push Docker images
        run: |
          docker compose -f docker-compose.prod.yml build
          docker compose -f docker-compose.prod.yml push
      - name: Deploy to server
        run: |
          ssh ${{ secrets.DEPLOY_HOST }} "cd /app && docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d"
```

---

## 9. Security-архитектура

### Аутентификация

| Механизм | Описание | Применение |
|----------|----------|-----------|
| JWT (Access Token) | Срок жизни 15 минут, в Authorization header | API-запросы |
| JWT (Refresh Token) | Срок жизни 7 дней, ротация при каждом обновлении | Обновление access token |
| Session Auth | Django session (cookie-based) | Unfold Admin панель |
| OTP (Telegram) | 6-значный код, срок жизни 5 минут, максимум 3 попытки | Вход через Telegram |

### JWT-конфигурация

```python
# config/settings/base.py
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "TOKEN_OBTAIN_SERIALIZER": "apps.accounts.serializers.CustomTokenObtainPairSerializer",
}
```

### Поток аутентификации

```
1. Вход через email/пароль:
   POST /api/v1/auth/login/ {email, password}
   → 200 {access, refresh, user}

2. Вход через Telegram OTP:
   POST /api/v1/auth/otp/request/ {telegram_id}
   → Telegram Bot отправляет 6-значный код
   POST /api/v1/auth/otp/verify/ {telegram_id, code}
   → 200 {access, refresh, user}

3. Обновление токена:
   POST /api/v1/auth/refresh/ {refresh}
   → 200 {access, refresh}  (старый refresh попадает в blacklist)

4. Выход:
   POST /api/v1/auth/logout/ {refresh}
   → Refresh token в blacklist
```

### Поток регистрации нового сотрудника

```
HR создаёт Employee в системе (email обязателен)
    │
    ▼
Система отправляет invite-ссылку на email
    │
    ▼
Сотрудник переходит по ссылке → страница установки пароля
    │
    ▼
Сотрудник заполняет профиль (ProfileCompletion)
    │
    ▼
Сотрудник принимает оферту (OfferAcceptance)
    │
    ▼
Аккаунт ожидает одобрения HR (PendingApproval)
    │
    ▼
HR одобряет → is_approved = True → доступ к системе
```

### CORS

```python
# development.py
CORS_ALLOW_ALL_ORIGINS = True

# production.py
CORS_ALLOWED_ORIGINS = [
    "https://uni-hrm.example.uz",
    "https://admin.uni-hrm.example.uz",
]
CORS_ALLOW_CREDENTIALS = True
```

### Rate Limiting

```python
# config/settings/base.py
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "20/minute",       # Неаутентифицированные
        "user": "100/minute",      # Аутентифицированные
        "login": "5/minute",       # Попытки входа
        "otp": "3/minute",         # Запросы OTP
    },
}
```

### Заголовки безопасности

```python
# config/settings/production.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy (django-csp)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
```

### Валидация данных

```python
# apps/core/validators.py

def validate_pinfl(value: str) -> str:
    """Валидация ПИНФЛ (14 цифр)."""
    if not value.isdigit() or len(value) != 14:
        raise ValidationError(_("ПИНФЛ должен содержать ровно 14 цифр"))
    return value

def validate_inn(value: str) -> str:
    """Валидация ИНН (9 цифр)."""
    if not value.isdigit() or len(value) != 9:
        raise ValidationError(_("ИНН должен содержать ровно 9 цифр"))
    return value

def validate_phone(value: str) -> str:
    """Валидация узбекистанского номера телефона."""
    pattern = r"^\+998[0-9]{9}$"
    if not re.match(pattern, value):
        raise ValidationError(_("Формат: +998XXXXXXXXX"))
    return value
```

### Защита файлов

- Загруженные файлы (резюме, сертификаты) хранятся в `MEDIA_ROOT` и доступны только аутентифицированным пользователям
- Максимальный размер файла: 20 MB
- Допустимые расширения: pdf, doc, docx, jpg, jpeg, png
- Файлы сканируются на наличие вредоносного содержимого (опционально, через ClamAV)

---

## 10. Интеграции

### HEMIS (Higher Education Management Information System)

HEMIS -- государственная информационная система управления высшим образованием Узбекистана.

**Тип интеграции:** OAuth 2.0 + REST API

```
┌──────────┐     OAuth 2.0      ┌──────────┐
│ uni-hrm  │◄──────────────────▶│  HEMIS   │
│          │     REST API       │  API     │
│          │◄──────────────────▶│          │
└──────────┘                    └──────────┘
```

**Возможности:**
- OAuth-авторизация сотрудников через HEMIS-аккаунт
- Синхронизация данных сотрудников (ФИО, должности, кафедры)
- Получение академической нагрузки
- Синхронизация списка кафедр и факультетов
- Периодическая фоновая синхронизация (Celery Beat, ежедневно в 2:00)

```python
# integrations/hemis/client.py
class HEMISClient:
    """Клиент для работы с HEMIS API."""

    def __init__(self):
        self.base_url = settings.HEMIS_API_URL
        self.client_id = settings.HEMIS_CLIENT_ID
        self.client_secret = settings.HEMIS_CLIENT_SECRET

    def get_oauth_url(self) -> str: ...
    def exchange_code(self, code: str) -> dict: ...
    def get_employee_data(self, hemis_id: str) -> dict: ...
    def sync_departments(self) -> list[dict]: ...
    def sync_employees(self) -> list[dict]: ...
```

### Telegram

**Два направления интеграции:**

1. **Telegram Gateway (OTP)** -- отправка одноразовых кодов через Telegram Bot API для двухфакторной аутентификации.

2. **Telegram Bot** -- полноценный бот для уведомлений и быстрых действий.

```
┌──────────┐    Bot API     ┌──────────┐     Webhook      ┌──────────┐
│ Telegram │◄──────────────▶│ Telegram │◄────────────────▶│ uni-hrm  │
│ User     │                │ Bot      │                   │ Backend  │
└──────────┘                └──────────┘                   └──────────┘
```

**Возможности бота:**
- Отправка OTP-кодов для аутентификации
- Уведомления о новых заявках на отпуск (для руководителей)
- Уведомления о статусе заявки (для сотрудников)
- Напоминания о приближающихся дедлайнах (конкурсы, аттестация)
- Уведомления о расчёте зарплаты

```python
# integrations/telegram/bot.py
class TelegramNotificationService:
    """Сервис отправки уведомлений через Telegram."""

    def send_otp(self, telegram_id: int, code: str) -> bool: ...
    def send_notification(self, telegram_id: int, message: str) -> bool: ...
    def send_leave_request_notification(self, leave_request: LeaveRequest) -> bool: ...
    def send_payroll_notification(self, employee: Employee, period: PayrollPeriod) -> bool: ...
```

---

## 11. Стек технологий

### Сводная таблица

| Слой | Технология | Назначение |
|------|-----------|-----------|
| **Backend** | Python 3.12 | Язык программирования |
| | Django 5.1 | Web-фреймворк |
| | Django REST Framework | REST API |
| | Django Unfold | Админ-панель |
| | djangorestframework-simplejwt | JWT-аутентификация |
| | django-mptt | Древовидные структуры (подразделения) |
| | django-filter | Фильтрация API |
| | django-cors-headers | CORS |
| | Celery 5.4 | Асинхронные задачи |
| | Redis 7 | Кеш + брокер Celery |
| | Jinja2 | Шаблоны документов |
| | uv | Package manager |
| **Frontend** | TypeScript 5.6 | Язык программирования |
| | React 19 | UI-фреймворк |
| | Vite 6 | Сборщик |
| | Tailwind CSS 4 | CSS-фреймворк |
| | shadcn/ui | UI-компоненты |
| | Zustand 5 | Управление состоянием |
| | TanStack Query 5 | Серверное состояние |
| | React Router 7 | Роутинг |
| | React Hook Form | Формы |
| | Zod | Валидация схем |
| | i18next | Локализация |
| | Recharts | Графики |
| | Axios | HTTP-клиент |
| **Database** | SQLite | Разработка |
| | PostgreSQL 16 | Продакшн |
| **Infrastructure** | Docker | Контейнеризация |
| | Docker Compose | Оркестрация |
| | Nginx | Reverse proxy + static |
| | GitHub Actions | CI/CD |
| **Мониторинг** | Sentry | Отслеживание ошибок |
| **Качество кода** | ruff | Python линтинг |
| | mypy | Python типизация |
| | Biome | TypeScript линтинг + форматирование |
| | pytest | Python тестирование |
| | Vitest | TypeScript тестирование |
