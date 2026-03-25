# Roadmap: Uni-HRM

> Дорожная карта разработки университетской системы управления персоналом

---

## Обзор фаз

```
Фаза 0: Инфраструктура ─────────────────────────────┐
                                                      │
Фаза 1: Auth + RBAC ─────────────────────────────────┤
                                                      │
         ┌────────────────────────────────────────────┤
         │                                            │
Фаза 2: Departments + Employees ─────────────────────┤
         │         │         │         │              │
         │         │         │         │              │
Фаза 3   Фаза 4   Фаза 5   Фаза 6   Фаза 11       │
Academic  Leaves   Attend.  Recruit.  Appraisal      │
         │         │                                  │
         │         │                                  │
         └────┬────┘                                  │
              │                                       │
Фаза 7: Payroll ─────────────────────────────────────┤
              │                                       │
Фаза 10: HEMIS Integration (← Фаза 2, 3)            │
              │                                       │
Фаза 8: Notifications + Telegram ────────────────────┤
              │                                       │
Фаза 9: Documents + Reports ─────────────────────────┘
```

### Диаграмма зависимостей (Gantt-стиль)

```
Месяц        1         2         3         4         5         6         7         8         9
           ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤
Фаза 0     ████████░░                                                               Инфраструктура
Фаза 1               ██████████░░                                                   Auth + RBAC
Фаза 2                         ████████████████░░                                   Departments + Employees
Фаза 3                                           ██████████░░                       Academic
Фаза 4                                           ████████░░                         Leaves
Фаза 5                                           ████████░░                         Attendance
Фаза 6                                           ████████░░                         Recruitment
Фаза 10                                                    ████████░░               HEMIS Integration
Фаза 11                                                    ██████████░░             Appraisal + Training
Фаза 7                                                     ██████████████░░         Payroll
Фаза 8                                                                   ████████░░ Notifications + TG
Фаза 9                                                                   ██████████ Documents + Reports
           ├─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┼─────────┤

░░ = буфер     ████ = активная разработка

Примечание: Фазы 3–6 и 10–11 могут выполняться параллельно разными разработчиками.
```

---

## Фаза 0: Инфраструктура

**Scope: L (Large)**
**Зависимости: нет**
**Длительность: ~3 недели**

### Описание

Фундаментальная фаза, закладывающая техническую основу проекта. Включает настройку Docker-окружения, CI/CD пайплайна, базовых абстрактных моделей Django, конфигурацию Tailwind CSS с дизайн-токенами из Figma, настройку интернационализации и scaffolding обоих приложений (backend + frontend).

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B0.1 | Инициализация Django-проекта | `django-admin startproject config`, структура `apps/`, настройка `settings/` (base, dev, prod) | — |
| B0.2 | Базовые абстрактные модели | `TimestampedModel` (UUID pk, created_at, updated_at), `SoftDeleteMixin` (is_deleted, deleted_at, soft_delete()), `ActiveManager` | B0.1 |
| B0.3 | Настройка DRF | DEFAULT_RENDERER_CLASSES, DEFAULT_PAGINATION_CLASS (PageNumberPagination, page_size=20), DEFAULT_FILTER_BACKENDS | B0.1 |
| B0.4 | Настройка django-unfold | Конфигурация UNFOLD в settings, кастомная тема с дизайн-токенами | B0.1 |
| B0.5 | Docker Compose | Dockerfile (multi-stage), docker-compose.yml (django, postgres, redis, celery worker, celery beat) | B0.1 |
| B0.6 | CI/CD (GitHub Actions) | Workflow: lint (ruff) → test (pytest) → build (Docker) → deploy | B0.5 |
| B0.7 | Backend i18n | Настройка `LANGUAGES`, `LOCALE_PATHS`, начальные `.po` файлы для ru, uz, en | B0.1 |
| B0.8 | Celery + Redis | Настройка celery.py, конфигурация CELERY_BROKER_URL, beat schedule | B0.5 |
| B0.9 | Утилиты и хелперы | `apps/core/`: pagination, exceptions, permissions base classes, response helpers | B0.2, B0.3 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F0.1 | Инициализация React + Vite + TS | `npm create vite@latest`, tsconfig strict, path aliases (@/) | — |
| F0.2 | Tailwind CSS с дизайн-токенами | tailwind.config.ts: цвета, шрифты, radius, spacing из Figma (TeamHub) | F0.1 |
| F0.3 | shadcn/ui | Установка и настройка, базовые компоненты: Button, Input, Card, Dialog, Table, Badge, Toast | F0.2 |
| F0.4 | Роутинг | React Router v7: layout routes (AuthLayout, DashboardLayout, SidebarLayout) | F0.1 |
| F0.5 | API-клиент | Axios instance с interceptors (JWT refresh, error handling), типизированные хелперы | F0.1 |
| F0.6 | TanStack Query | QueryClientProvider, default options, devtools | F0.5 |
| F0.7 | i18n (react-i18next) | Инициализация, JSON-файлы переводов (ru, uz, en), LanguageSwitcher компонент | F0.1 |
| F0.8 | Подключение шрифтов | Plus Jakarta Sans (body), Red Hat Display (headings) через Google Fonts | F0.2 |
| F0.9 | Общие компоненты | LoadingSpinner, ErrorBoundary, PageHeader, EmptyState, ConfirmDialog | F0.3 |

### Критерии приёмки

- [ ] `docker-compose up` запускает все сервисы без ошибок
- [ ] Django admin (unfold) доступен по `/admin/`
- [ ] DRF browsable API доступен по `/api/`
- [ ] Frontend dev-сервер запускается и отображает страницу
- [ ] Tailwind-стили применяются корректно (цвета, шрифты из Figma)
- [ ] i18n переключение языков работает на frontend
- [ ] GitHub Actions workflow проходит (lint + test)
- [ ] `TimestampedModel` и `SoftDeleteMixin` покрыты unit-тестами
- [ ] Celery worker принимает и обрабатывает тестовую задачу
- [ ] Ruff проходит без ошибок

---

## Фаза 1: Auth + RBAC

**Scope: L (Large)**
**Зависимости: Фаза 0**
**Длительность: ~3 недели**

### Описание

Система аутентификации и авторизации. Google OAuth 2.0 для входа, JWT-токены для API, Telegram OTP как второй фактор верификации. Ролевая модель с 8 ролями и гранулярными разрешениями. Полностью функциональные страницы входа и регистрации на frontend.

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B1.1 | Модель User | Кастомная модель User (AbstractUser): email как username, phone, avatar, language preference, is_verified | — |
| B1.2 | django-allauth + Google OAuth | Настройка SOCIALACCOUNT_PROVIDERS, callback URLs, создание User при первом входе | B1.1 |
| B1.3 | JWT (simplejwt) | ACCESS_TOKEN_LIFETIME=15min, REFRESH_TOKEN_LIFETIME=7days, TokenObtainPairView, TokenRefreshView | B1.1 |
| B1.4 | Модель Role | Role (name, code, description), Permission (codename, description), RolePermission (M2M), UserRole (FK) | B1.1 |
| B1.5 | Permission system | Кастомный permission backend, декораторы `@has_role()`, `@has_permission()`, DRF permission classes | B1.4 |
| B1.6 | Telegram OTP | Модель OTPCode (user, code, expires_at), генерация 6-значного кода, отправка через Telegram Bot API | B1.1 |
| B1.7 | API endpoints | `/api/auth/login/`, `/api/auth/register/`, `/api/auth/google/`, `/api/auth/refresh/`, `/api/auth/verify-otp/`, `/api/auth/me/` | B1.2, B1.3, B1.6 |
| B1.8 | Сериализаторы | LoginSerializer, RegisterSerializer, UserSerializer, RoleSerializer, ChangePasswordSerializer | B1.7 |
| B1.9 | Seed data | Management command `seed_roles` — создание 8 ролей с базовым набором разрешений | B1.4 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F1.1 | Auth store (Zustand) | useAuthStore: user, tokens, login(), logout(), refreshToken(), isAuthenticated | — |
| F1.2 | Страница Login | Email + пароль, кнопка "Войти через Google", ссылка на регистрацию, валидация (Zod) | F1.1 |
| F1.3 | Google OAuth flow | Redirect → Google → callback → сохранение токенов | F1.1 |
| F1.4 | Страница Register | Форма регистрации: ФИО, email, phone, password, подтверждение пароля | F1.1 |
| F1.5 | OTP верификация | Модальное окно с 6-значным кодом из Telegram, таймер повторной отправки (60 сек) | F1.1 |
| F1.6 | Protected Routes | PrivateRoute компонент: проверка isAuthenticated, redirect на /login | F1.1 |
| F1.7 | JWT interceptor | Axios interceptor: автоматический refresh при 401, очередь запросов | F1.1 |
| F1.8 | Профиль пользователя | Страница `/profile`: просмотр и редактирование, смена пароля, управление сессиями | F1.1 |
| F1.9 | Управление ролями (Admin) | Страница `/admin/roles`: CRUD для ролей, матрица разрешений, назначение ролей пользователям | F1.1 |

### Критерии приёмки

- [ ] Вход через email + пароль работает
- [ ] Вход через Google OAuth 2.0 работает
- [ ] JWT-токены выдаются и автоматически обновляются
- [ ] Telegram OTP отправляется и верифицируется
- [ ] 8 ролей созданы через seed command
- [ ] Unauthorized пользователь перенаправляется на /login
- [ ] Permission checks работают на уровне API
- [ ] Тесты: регистрация, вход, refresh token, permission denied
- [ ] Rate limiting на `/api/auth/login/` (5 попыток в минуту)

---

## Фаза 2: Departments + Employees

**Scope: XL (Extra Large)**
**Зависимости: Фаза 1**
**Длительность: ~4 недели**

### Описание

Ядро системы — модуль подразделений и сотрудников. MPTT-дерево подразделений (университет → факультет → кафедра → отдел), модель должностей с категориями, полная модель сотрудника со всеми необходимыми полями (персональные данные, образование, контакты, документы). Интерактивная организационная структура (d3-org-chart), справочник сотрудников с расширенной фильтрацией и поиском.

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B2.1 | Модель Department | MPTT-дерево: name (JSONField i18n), code, parent, level, department_type (faculty/department/division/unit), head (FK → Employee), is_active | — |
| B2.2 | Модель Position | name (JSONField i18n), code, category (ППС/АУП/УВП/ХП), min_salary, max_salary, is_academic, requirements | — |
| B2.3 | Модель Employee | Полная модель: user (OneToOne), employee_number, department, position, hire_date, contract_type (штат/совместитель/почасовик), status (active/on_leave/dismissed), personal data (ИНН, ПИНФЛ, паспорт), education, contacts, photo | B2.1, B2.2 |
| B2.4 | Модель EmploymentHistory | employee, department, position, start_date, end_date, order_number, order_date — история переводов | B2.3 |
| B2.5 | Department API | DepartmentViewSet (CRUD, tree endpoint, children, employees count), DepartmentSerializer (nested tree) | B2.1 |
| B2.6 | Position API | PositionViewSet (CRUD, filter by category), PositionSerializer | B2.2 |
| B2.7 | Employee API | EmployeeViewSet (CRUD, list with filters, search, export), EmployeeSerializer (list/detail), EmployeeCreateSerializer | B2.3 |
| B2.8 | Фильтрация и поиск | EmployeeFilter (department, position, status, category, hire_date range), SearchFilter (ФИО, табельный номер) | B2.7 |
| B2.9 | Org chart endpoint | `/api/departments/org-chart/` — дерево подразделений с руководителями для d3-org-chart | B2.5 |
| B2.10 | Employee import/export | Celery task: импорт сотрудников из Excel (openpyxl), экспорт списка в Excel | B2.7 |
| B2.11 | Signals и автоматизация | Post-save: генерация employee_number, создание EmploymentHistory при изменении department/position | B2.3 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F2.1 | Справочник подразделений | Страница `/departments`: дерево подразделений (TreeView), CRUD, drag-n-drop для перемещения | — |
| F2.2 | Организационная структура | Страница `/org-chart`: интерактивная визуализация (d3-org-chart), zoom, pan, клик на узел → детали | — |
| F2.3 | Список сотрудников | Страница `/employees`: TanStack Table, пагинация, сортировка, фильтры (department, position, status, category) | — |
| F2.4 | Поиск сотрудников | Глобальный поиск с debounce (300ms), search по ФИО и табельному номеру, autocomplete | F2.3 |
| F2.5 | Карточка сотрудника | Страница `/employees/:id`: табы (Основное, Образование, Документы, История, Отпуска), фото, статус | — |
| F2.6 | Создание сотрудника | Мультишаговая форма (React Hook Form + Zod): 1) Персональные данные 2) Должность 3) Документы 4) Контакты | — |
| F2.7 | Редактирование сотрудника | Inline-редактирование полей, модальные окна для секций, валидация | F2.5 |
| F2.8 | Справочник должностей | Страница `/positions`: CRUD таблица, фильтр по категории персонала | — |
| F2.9 | Импорт/Экспорт | Кнопка "Экспорт в Excel" на странице списка, модалка "Импорт из Excel" с drag-n-drop зоной | F2.3 |
| F2.10 | Employee store (TanStack Query) | Хуки: useEmployees(), useEmployee(id), useCreateEmployee(), useUpdateEmployee(), useDeleteEmployee() | — |
| F2.11 | Department store (TanStack Query) | Хуки: useDepartments(), useDepartmentTree(), useOrgChart() | — |

### Критерии приёмки

- [ ] MPTT-дерево подразделений корректно создаётся и отображается
- [ ] CRUD для подразделений и должностей работает
- [ ] Полный CRUD для сотрудников (создание через мультишаговую форму)
- [ ] Организационная структура отображается корректно (d3-org-chart)
- [ ] Фильтрация по всем критериям работает
- [ ] Поиск по ФИО и табельному номеру работает
- [ ] Импорт из Excel обрабатывает минимум 500 записей без ошибок
- [ ] Экспорт в Excel включает все фильтры
- [ ] История изменений сотрудника (django-simple-history) записывается
- [ ] Soft delete работает корректно
- [ ] Тесты: CRUD, фильтрация, импорт/экспорт, permission checks
- [ ] select_related/prefetch_related оптимизированы (нет N+1)

---

## Фаза 3: Academic Module

**Scope: M (Medium)**
**Зависимости: Фаза 2**
**Длительность: ~2.5 недели**

### Описание

Модуль академической деятельности, специфичный для университетов. Учёные степени (кандидат наук, доктор наук, PhD, DSc), учёные звания (доцент, профессор), дисциплины, расчёт учебной нагрузки ППС, конкурсы на замещение вакантных должностей. Позволяет деканатам и кафедрам управлять академическими данными преподавателей.

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B3.1 | Модель AcademicDegree | name (JSONField i18n), code (PhD, DSc, кандидат, доктор), country, year_awarded | — |
| B3.2 | Модель AcademicTitle | name (JSONField i18n), code (доцент, профессор, старший научный сотрудник) | — |
| B3.3 | Модель EmployeeAcademic | employee (FK), degree (FK), title (FK), specialization, dissertation_topic, diploma_number, awarded_date | B3.1, B3.2 |
| B3.4 | Модель Subject | name (JSONField i18n), code, department (FK), credits, semester, is_active | — |
| B3.5 | Модель AcademicLoad | employee (FK), subject (FK), academic_year, semester, lecture_hours, seminar_hours, lab_hours, total_hours, load_type (основная/дополнительная) | B3.4 |
| B3.6 | Расчёт нагрузки | Service: calculate_total_load(employee, academic_year) — автоматический расчёт общей нагрузки с учётом нормативов (максимум 900 часов/год для ППС) | B3.5 |
| B3.7 | Модель PositionContest | department, position, requirements, application_deadline, status (open/reviewing/closed), winner (FK → Employee) | — |
| B3.8 | API endpoints | AcademicDegreeViewSet, AcademicTitleViewSet, SubjectViewSet, AcademicLoadViewSet, PositionContestViewSet | B3.1–B3.7 |
| B3.9 | Сериализаторы | Nested serializers для academic data, LoadSummarySerializer (агрегация по преподавателю) | B3.8 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F3.1 | Академические данные в карточке сотрудника | Таб "Академическая деятельность": степень, звание, специализация, нагрузка | — |
| F3.2 | Справочники | Страницы CRUD: учёные степени, учёные звания, дисциплины | — |
| F3.3 | Учебная нагрузка | Таблица распределения нагрузки по преподавателям, фильтр по кафедре, году, семестру | — |
| F3.4 | Расчёт нагрузки | Визуализация: прогресс-бар загруженности (текущая/максимальная), предупреждение при превышении | F3.3 |
| F3.5 | Конкурсы на замещение | Страница `/contests`: список конкурсов, карточка конкурса, подача заявки, статус pipeline | — |
| F3.6 | TanStack Query хуки | useAcademicLoad(), useSubjects(), useContests() | — |

### Критерии приёмки

- [ ] CRUD для учёных степеней, званий, дисциплин работает
- [ ] Учебная нагрузка рассчитывается корректно
- [ ] Предупреждение при превышении максимальной нагрузки (900 ч/год)
- [ ] Конкурсы на замещение: полный workflow (создание → приём заявок → закрытие)
- [ ] Академические данные отображаются в карточке сотрудника
- [ ] Тесты: расчёт нагрузки, валидация конкурсов

---

## Фаза 4: Leaves (Отпуска)

**Scope: M (Medium)**
**Зависимости: Фаза 2**
**Длительность: ~2.5 недели**

### Описание

Модуль управления отпусками с учётом специфики узбекского трудового законодательства. Различные типы отпусков с разными нормативами (56 дней для ППС, 24 дня для АУП), автоматический расчёт накопленных дней, двухуровневое согласование (руководитель → HR), календарь отпусков подразделения.

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B4.1 | Модель LeaveType | name (JSONField i18n), code, days_per_year, is_paid, requires_document, applicable_categories (JSONField: ["ППС", "АУП"]) | — |
| B4.2 | Seed: типы отпусков | Ежегодный (ППС: 56 дней, АУП: 24 дня), учебный, без сохранения зарплаты, по беременности, по болезни, творческий (для докторантов) | B4.1 |
| B4.3 | Модель LeaveAllocation | employee (FK), leave_type (FK), year, total_days, used_days, remaining_days (property), carry_over_days | B4.1 |
| B4.4 | Auto-allocation | Celery task (ежегодный, 1 января): автоматическое начисление дней отпуска на новый год на основе категории и стажа | B4.3 |
| B4.5 | Модель LeaveRequest | employee (FK), leave_type (FK), start_date, end_date, days_count (auto-calculated), reason, status (draft/pending_head/pending_hr/approved/rejected), approved_by, rejection_reason | B4.3 |
| B4.6 | Two-level approval | Workflow: сотрудник → руководитель подразделения (pending_head) → HR Manager (pending_hr) → approved/rejected | B4.5 |
| B4.7 | Валидация | Проверки: достаточно дней, нет пересечений с другими отпусками, не более N сотрудников одновременно | B4.5 |
| B4.8 | API endpoints | LeaveTypeViewSet, LeaveAllocationViewSet, LeaveRequestViewSet (create, approve, reject, cancel) | B4.1–B4.7 |
| B4.9 | Calendar endpoint | `/api/leaves/calendar/?department=X&month=Y` — отпуска подразделения за месяц | B4.5 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F4.1 | Мои отпуска | Страница `/leaves`: список заявлений, баланс дней по типам (прогресс-бары), история | — |
| F4.2 | Создание заявления | Модальная форма: тип отпуска, даты (date range picker), причина, автоматический расчёт дней | — |
| F4.3 | Согласование отпусков | Страница `/leaves/approval`: список заявлений на согласование (для руководителей и HR), approve/reject с комментарием | — |
| F4.4 | Календарь отпусков | Страница `/leaves/calendar`: визуализация отпусков подразделения (горизонтальная timeline), фильтр по отделу | — |
| F4.5 | Баланс отпусков в карточке сотрудника | Таб "Отпуска": баланс, история заявлений, статистика | — |
| F4.6 | TanStack Query хуки | useLeaveBalance(), useLeaveRequests(), useApproveLeave(), useRejectLeave() | — |

### Критерии приёмки

- [ ] Типы отпусков с разным количеством дней по категориям
- [ ] Автоматическое начисление дней отпуска (Celery task)
- [ ] Создание заявления с автоматическим расчётом дней (исключая выходные)
- [ ] Двухуровневое согласование работает (руководитель → HR)
- [ ] Валидация: нельзя взять больше дней, чем начислено
- [ ] Валидация: проверка пересечений с другими отпусками
- [ ] Календарь отпусков подразделения отображается корректно
- [ ] Уведомления при смене статуса заявления
- [ ] Тесты: allocation, approval workflow, валидации, edge cases

---

## Фаза 5: Attendance (Табель)

**Scope: M (Medium)**
**Зависимости: Фаза 2**
**Длительность: ~2.5 недели**

### Описание

Модуль учёта рабочего времени. Шаблоны рабочих графиков (5/2, 6/1, сменный), ежедневная отметка прихода/ухода, месячный табель с агрегированными данными, возможность импорта данных из внешних систем контроля доступа (турникеты, биометрия).

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B5.1 | Модель WorkSchedule | name, schedule_type (5/2, 6/1, shift, flexible), work_start, work_end, break_start, break_end, working_days (JSONField: [1,2,3,4,5]) | — |
| B5.2 | Модель EmployeeSchedule | employee (FK), schedule (FK), effective_from, effective_to — привязка графика к сотруднику | B5.1 |
| B5.3 | Модель AttendanceRecord | employee (FK), date, check_in, check_out, status (present/absent/late/half_day/on_leave/holiday), worked_hours (auto), overtime_hours, source (manual/import/biometric) | — |
| B5.4 | Модель TimeSheet | employee (FK), month, year, total_working_days, days_present, days_absent, days_late, total_hours, overtime_hours, status (draft/submitted/approved) | B5.3 |
| B5.5 | TimeSheet aggregation | Celery task (ежемесячный): автоматическая генерация TimeSheet из AttendanceRecord за прошедший месяц | B5.4 |
| B5.6 | Import from external | Management command + API endpoint: импорт из CSV/Excel (формат: employee_number, date, check_in, check_out) | B5.3 |
| B5.7 | API endpoints | WorkScheduleViewSet, AttendanceRecordViewSet (bulk create), TimeSheetViewSet (submit, approve) | B5.1–B5.6 |
| B5.8 | Holidays | Модель Holiday (date, name, is_working_day), учёт государственных праздников Узбекистана | — |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F5.1 | Рабочие графики | Страница `/schedules`: CRUD, визуализация недельного графика | — |
| F5.2 | Журнал посещаемости | Страница `/attendance`: таблица за день/неделю, bulk-редактирование, цветовая кодировка статусов | — |
| F5.3 | Табель (TimeSheet) | Страница `/timesheet`: месячный табель по подразделению, формат Т-13, submit/approve workflow | — |
| F5.4 | Импорт данных | Модальное окно: upload CSV/Excel, preview, подтверждение, отчёт об импорте (успешно/ошибки) | — |
| F5.5 | Моя посещаемость (Employee) | Виджет в профиле: мой график, статистика за месяц, опоздания | — |
| F5.6 | TanStack Query хуки | useAttendance(), useTimeSheet(), useWorkSchedules() | — |

### Критерии приёмки

- [ ] Шаблоны рабочих графиков (5/2, 6/1, сменный) создаются и назначаются
- [ ] Запись прихода/ухода работает (manual + bulk)
- [ ] Автоматический расчёт отработанных часов и переработок
- [ ] Месячный табель генерируется автоматически
- [ ] Учёт государственных праздников Узбекистана
- [ ] Импорт из CSV/Excel с отчётом об ошибках
- [ ] Табель: submit → approve workflow
- [ ] Тесты: расчёт часов, агрегация, импорт

---

## Фаза 6: Recruitment (Рекрутинг)

**Scope: M (Medium)**
**Зависимости: Фаза 2**
**Длительность: ~2.5 недели**

### Описание

Модуль подбора персонала. Публикация вакансий, приём заявок кандидатов, отслеживание статуса через pipeline (заявка → HR-скрининг → собеседование → оффер → найм), Kanban-доска для HR-менеджеров.

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B6.1 | Модель Vacancy | department (FK), position (FK), title, description, requirements, salary_range_min/max, status (draft/open/closed/on_hold), published_at, deadline | — |
| B6.2 | Модель Candidate | full_name, email, phone, resume (FileField), cover_letter, source (website/referral/hemis/other) | — |
| B6.3 | Модель CandidateApplication | vacancy (FK), candidate (FK), status (new/screening/interview/offer/hired/rejected), applied_at, notes | B6.1, B6.2 |
| B6.4 | Модель InterviewStage | application (FK), stage_type (phone/technical/hr/final), scheduled_at, interviewer (FK → Employee), feedback, score (1-10), result (pass/fail/pending) | B6.3 |
| B6.5 | Vacancy API | VacancyViewSet (CRUD, publish, close), public endpoint для внешних кандидатов | B6.1 |
| B6.6 | Candidate API | CandidateViewSet, CandidateApplicationViewSet (apply, change_status), InterviewStageViewSet | B6.2–B6.4 |
| B6.7 | Pipeline transitions | Валидация переходов статуса (new → screening → interview → offer → hired), автоматическое создание Employee при hired | B6.3 |
| B6.8 | Statistics endpoint | `/api/recruitment/stats/` — воронка найма, среднее время закрытия вакансии, количество по статусам | B6.3 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F6.1 | Список вакансий | Страница `/vacancies`: таблица вакансий, фильтр по статусу/отделу, создание/редактирование | — |
| F6.2 | Карточка вакансии | Страница `/vacancies/:id`: описание, требования, список кандидатов, статистика | — |
| F6.3 | Kanban-доска | Страница `/recruitment/board`: колонки по статусам (New → Screening → Interview → Offer → Hired), drag-n-drop карточки кандидатов | — |
| F6.4 | Карточка кандидата | Модальное окно: данные кандидата, загруженное резюме, история собеседований, timeline | — |
| F6.5 | Форма подачи заявки (Public) | Публичная страница: форма для внешнего кандидата (без аутентификации), upload резюме | — |
| F6.6 | Воронка найма | Dashboard виджет: Recharts funnel chart — конверсия по этапам | — |
| F6.7 | TanStack Query хуки | useVacancies(), useCandidates(), useRecruitmentStats() | — |

### Критерии приёмки

- [ ] CRUD вакансий с публикацией и закрытием
- [ ] Публичная форма подачи заявки (без авторизации)
- [ ] Kanban-доска с drag-n-drop перемещением кандидатов
- [ ] Pipeline статусов с валидацией переходов
- [ ] Запись собеседований с оценкой
- [ ] Автоматическое создание Employee при статусе "hired"
- [ ] Воронка найма (статистика конверсии)
- [ ] Тесты: pipeline transitions, permission checks

---

## Фаза 7: Payroll (Зарплата)

**Scope: XL (Extra Large)**
**Зависимости: Фазы 2, 3, 4, 5**
**Длительность: ~4 недели**

### Описание

Модуль расчёта заработной платы с учётом узбекского налогового законодательства. Тарифные сетки, надбавки (за учёную степень, стаж, совмещение), расчёт зарплаты с учётом отработанных дней, отпускных, больничных. Расчёт налогов: НДФЛ 12%, пенсионный взнос 8%. Формирование расчётных листков и ведомостей.

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B7.1 | Модель SalaryGrade | name, grade_level, base_salary, currency (UZS), effective_from | — |
| B7.2 | Модель Allowance | name (JSONField i18n), code, allowance_type (fixed/percentage), amount, percentage, is_taxable, applicable_to (JSONField: условия) | — |
| B7.3 | Модель EmployeeSalary | employee (FK), salary_grade (FK), base_salary, effective_from, effective_to, allowances (M2M → Allowance) | B7.1, B7.2 |
| B7.4 | Seed: надбавки | За PhD (+15%), за DSc (+25%), за стаж (5-10лет: +10%, 10-20: +15%, 20+: +20%), за совмещение, за вредность, за интенсивность | B7.2 |
| B7.5 | Модель PayrollPeriod | month, year, status (draft/calculating/calculated/approved/paid), created_by, approved_by, approved_at | — |
| B7.6 | Модель PayrollEntry | payroll_period (FK), employee (FK), base_salary, allowances_total, gross_salary, deductions (JSONField), ndfl_amount (12%), pension_amount (8%), net_salary, working_days, actual_days, overtime_hours, overtime_amount | B7.5 |
| B7.7 | Payroll calculation service | PayrollCalculator: calculate_for_employee(employee, period) → PayrollEntry. Учёт: рабочих дней (из TimeSheet), отпускных (из LeaveRequest), больничных, надбавок, налогов | B7.6 |
| B7.8 | Bulk calculation | Celery task: calculate_payroll(period_id) — расчёт для всех активных сотрудников | B7.7 |
| B7.9 | Payslip endpoint | `/api/payroll/payslip/:employee_id/:period_id/` — расчётный листок сотрудника | B7.6 |
| B7.10 | API endpoints | SalaryGradeViewSet, AllowanceViewSet, PayrollPeriodViewSet (create, calculate, approve), PayrollEntryViewSet (read-only) | B7.1–B7.9 |
| B7.11 | Ведомости | Celery task: генерация Excel-ведомости по подразделению (сводная, развёрнутая) | B7.6 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F7.1 | Тарифные сетки | Страница `/payroll/grades`: CRUD таблица, история изменений | — |
| F7.2 | Надбавки | Страница `/payroll/allowances`: справочник надбавок, привязка к сотрудникам | — |
| F7.3 | Расчётный период | Страница `/payroll/periods`: список периодов, создание, запуск расчёта, утверждение | — |
| F7.4 | Расчётная ведомость | Страница `/payroll/periods/:id`: таблица всех сотрудников за период, сортировка, фильтры, итоговые суммы | — |
| F7.5 | Расчётный листок | Компонент PayslipCard: детализация начислений и удержаний, возможность печати/PDF | — |
| F7.6 | Мой расчётный листок (Employee) | Страница `/my/payslip`: просмотр своих расчётных листков по периодам | — |
| F7.7 | Зарплатная аналитика | Dashboard виджет: ФОТ по подразделениям (bar chart), динамика ФОТ (line chart), средняя зарплата по категориям | — |
| F7.8 | Экспорт ведомостей | Кнопка "Экспорт в Excel" — сводная и развёрнутая ведомости | — |
| F7.9 | TanStack Query хуки | usePayrollPeriods(), usePayrollEntries(), usePayslip(), useSalaryGrades() | — |

### Критерии приёмки

- [ ] Тарифные сетки и надбавки CRUD работает
- [ ] Расчёт зарплаты учитывает: оклад + надбавки − НДФЛ(12%) − пенсионный(8%)
- [ ] Расчёт учитывает фактически отработанные дни (из табеля)
- [ ] Отпускные рассчитываются корректно
- [ ] Bulk calculation через Celery для всех сотрудников
- [ ] Расчётный листок доступен каждому сотруднику
- [ ] Экспорт ведомости в Excel
- [ ] Workflow: draft → calculating → calculated → approved → paid
- [ ] Тесты: расчёт зарплаты (различные сценарии), налоги, надбавки, edge cases

---

## Фаза 8: Notifications + Telegram

**Scope: L (Large)**
**Зависимости: все предыдущие фазы**
**Длительность: ~3 недели**

### Описание

Система уведомлений — как в приложении (in-app), так и через Telegram. Шаблоны уведомлений с поддержкой переменных. Telegram-бот для HR-алертов, согласования отпусков, просмотра зарплатных листков. Telegram Mini App для мобильного доступа к основным функциям.

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B8.1 | Модель NotificationTemplate | code, name, subject (JSONField i18n), body (JSONField i18n), channels (JSONField: ["in_app", "telegram", "email"]), variables (JSONField: описание переменных) | — |
| B8.2 | Модель Notification | user (FK), template (FK), title, message, channel (in_app/telegram/email), is_read, read_at, data (JSONField: context) | B8.1 |
| B8.3 | Notification service | NotificationService.send(user, template_code, context) — рендеринг шаблона, отправка по каналам | B8.2 |
| B8.4 | Django Channels (WebSocket) | Consumer: NotificationConsumer — real-time push уведомлений, счётчик непрочитанных | B8.2 |
| B8.5 | Telegram Bot (aiogram 3.x) | Bot: команды (/start, /link, /leaves, /payslip), inline keyboards, обработка callback | — |
| B8.6 | Модель TelegramUser | user (OneToOne), telegram_id, chat_id, is_active, linked_at | B8.5 |
| B8.7 | Telegram уведомления | Celery task: send_telegram_notification(telegram_id, message) | B8.5, B8.6 |
| B8.8 | Telegram Mini App backend | API endpoints для Mini App: /api/telegram/auth/, /api/telegram/me/, simplified endpoints | B8.6 |
| B8.9 | Seed: шаблоны уведомлений | Шаблоны: leave_request_created, leave_approved, leave_rejected, payslip_ready, contract_expiring, birthday | B8.1 |
| B8.10 | Notification API | NotificationViewSet (list, mark_read, mark_all_read, unread_count) | B8.2 |
| B8.11 | Интеграция с модулями | Сигналы: при создании/одобрении LeaveRequest, при расчёте зарплаты, при истечении договора | B8.3 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F8.1 | Notification bell | Компонент в хедере: иконка колокольчика, badge с количеством непрочитанных, dropdown список | — |
| F8.2 | WebSocket подключение | Автоматическое подключение при аутентификации, reconnect при разрыве | — |
| F8.3 | Notification center | Страница `/notifications`: полный список, фильтр по типу/статусу, mark as read, bulk actions | — |
| F8.4 | Toast уведомления | Real-time toast при получении нового уведомления через WebSocket | F8.2 |
| F8.5 | Управление шаблонами (Admin) | Страница `/admin/notification-templates`: редактирование шаблонов, preview, тестовая отправка | — |
| F8.6 | Telegram привязка | Компонент в профиле: "Привязать Telegram" — QR-код или deep link, статус привязки | — |
| F8.7 | Notification store | useNotifications(), useUnreadCount(), useMarkAsRead() | — |

### Критерии приёмки

- [ ] In-app уведомления доставляются в real-time (WebSocket)
- [ ] Telegram-бот отвечает на команды (/start, /link, /leaves, /payslip)
- [ ] Привязка Telegram-аккаунта работает
- [ ] Telegram-уведомления отправляются при событиях (отпуска, зарплата)
- [ ] Шаблоны уведомлений поддерживают переменные и мультиязычность
- [ ] Счётчик непрочитанных обновляется в real-time
- [ ] Mark as read / mark all as read работает
- [ ] Telegram Mini App авторизация через initData
- [ ] Тесты: отправка уведомлений, WebSocket, Telegram bot handlers

---

## Фаза 9: Documents + Reports

**Scope: L (Large)**
**Зависимости: Фазы 7, 8**
**Длительность: ~3 недели**

### Описание

Модуль генерации документов и аналитической отчётности. Шаблоны документов (приказы, трудовые договоры, справки) с Jinja2 и генерацией PDF через WeasyPrint. Excel-отчёты для бухгалтерии и руководства (openpyxl). Аналитический дашборд с ключевыми метриками HR.

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B9.1 | Модель DocumentTemplate | name, code (hiring_order, dismissal_order, contract, reference), template_file (Jinja2 HTML), variables_schema (JSONField), output_format (pdf/docx) | — |
| B9.2 | Модель GeneratedDocument | template (FK), employee (FK), generated_by (FK → User), file (FileField), data (JSONField: использованные данные), generated_at | B9.1 |
| B9.3 | Document generation service | DocumentGenerator.generate(template_code, employee_id, extra_data) → PDF file. Jinja2 рендеринг → WeasyPrint → PDF | B9.1, B9.2 |
| B9.4 | Seed: шаблоны документов | Приказ о приёме, приказ об увольнении, трудовой договор, справка с места работы, приказ об отпуске | B9.1 |
| B9.5 | Report service | ReportGenerator: generate_payroll_report(period, department), generate_employee_report(filters), generate_attendance_report(month) → Excel (openpyxl) | — |
| B9.6 | Analytics endpoints | `/api/analytics/dashboard/` — сводные метрики: общее количество сотрудников, текучесть кадров, средний стаж, ФОТ, отпуска | — |
| B9.7 | Analytics: детализация | `/api/analytics/turnover/`, `/api/analytics/demographics/`, `/api/analytics/department-stats/` | B9.6 |
| B9.8 | Document API | DocumentTemplateViewSet (list, preview), GeneratedDocumentViewSet (generate, download, list) | B9.1–B9.3 |
| B9.9 | Scheduled reports | Celery beat: ежемесячный отчёт для HR, ежеквартальный для ректората | B9.5 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F9.1 | Шаблоны документов | Страница `/documents/templates`: список шаблонов, предпросмотр, редактирование (Admin) | — |
| F9.2 | Генерация документа | Модальная форма: выбор шаблона, выбор сотрудника, дополнительные поля из variables_schema, кнопка "Сгенерировать" | — |
| F9.3 | Мои документы (Employee) | Страница `/my/documents`: список сгенерированных документов, скачивание PDF | — |
| F9.4 | Реестр документов | Страница `/documents`: все сгенерированные документы, фильтры (тип, дата, сотрудник), поиск | — |
| F9.5 | HR Dashboard | Страница `/dashboard`: KPI-карточки (сотрудники, вакансии, отпуска, ФОТ), графики (Recharts) | — |
| F9.6 | Аналитика: текучесть кадров | Страница `/analytics/turnover`: line chart по месяцам, breakdown по причинам увольнения | — |
| F9.7 | Аналитика: демография | Страница `/analytics/demographics`: pie charts (возраст, пол, образование), bar charts (стаж, категории) | — |
| F9.8 | Аналитика: по подразделениям | Страница `/analytics/departments`: штатная vs фактическая численность, средняя зарплата, вакансии | — |
| F9.9 | Отчёты (Excel) | Страница `/reports`: генерация Excel-отчётов по выбранным параметрам, скачивание | — |
| F9.10 | TanStack Query хуки | useDashboardStats(), useTurnoverAnalytics(), useDocumentTemplates(), useGenerateDocument() | — |

### Критерии приёмки

- [ ] Шаблоны документов (Jinja2) хранятся в БД и редактируются
- [ ] PDF генерируется корректно (WeasyPrint) с правильной кодировкой UTF-8
- [ ] Приказ о приёме, увольнении, отпуске генерируются с реальными данными сотрудника
- [ ] Excel-отчёты формируются с фильтрами (подразделение, период, категория)
- [ ] HR Dashboard отображает актуальные KPI
- [ ] Аналитика текучести рассчитывается корректно
- [ ] Scheduled reports отправляются по расписанию (Celery beat)
- [ ] Тесты: генерация PDF, расчёт аналитики, Excel-отчёты

---

## Фаза 10: HEMIS Integration

**Scope: M (Medium)**
**Зависимости: Фазы 2, 3**
**Длительность: ~2.5 недели**

### Описание

Интеграция с государственной системой HEMIS (Higher Education Management Information System). OAuth-авторизация через univer.hemis.uz, синхронизация справочников (подразделения, должности), импорт данных сотрудников и учебной нагрузки из HEMIS API. Обеспечивает соответствие данных университета государственным требованиям.

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B10.1 | HEMIS OAuth provider | django-allauth socialaccount provider для HEMIS OAuth 2.0 (univer.hemis.uz/oauth/authorize) | — |
| B10.2 | HEMIS API client | HEMISClient: обёртка над HEMIS REST API, authenticated requests, error handling, rate limiting | — |
| B10.3 | Модель HEMISMapping | content_type (FK), object_id (UUID), hemis_id (str), last_synced_at, sync_status (success/error/pending) — маппинг локальных объектов на HEMIS ID | — |
| B10.4 | Sync: Departments | Celery task: sync_departments_from_hemis() — импорт факультетов, кафедр, отделов с маппингом | B10.2, B10.3 |
| B10.5 | Sync: Employees | Celery task: sync_employees_from_hemis() — импорт/обновление сотрудников, сопоставление по ПИНФЛ | B10.2, B10.3 |
| B10.6 | Sync: Academic Loads | Celery task: sync_academic_loads_from_hemis() — импорт учебной нагрузки, дисциплин | B10.2, B10.3 |
| B10.7 | Conflict resolution | При конфликтах (данные в HEMIS != локальные): создание SyncConflict записи для ручного разрешения | B10.4–B10.6 |
| B10.8 | API endpoints | `/api/integrations/hemis/sync/` (trigger sync), `/api/integrations/hemis/status/` (sync status), `/api/integrations/hemis/conflicts/` (list/resolve conflicts) | B10.1–B10.7 |
| B10.9 | Scheduled sync | Celery beat: ежедневная синхронизация в 03:00, еженедельный полный пересчёт | B10.4–B10.6 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F10.1 | Настройки HEMIS | Страница `/settings/hemis`: конфигурация OAuth, URL API, тестирование подключения | — |
| F10.2 | Панель синхронизации | Страница `/integrations/hemis`: статус последней синхронизации, кнопка "Синхронизировать сейчас", progress bar | — |
| F10.3 | Разрешение конфликтов | Страница `/integrations/hemis/conflicts`: таблица конфликтов, сравнение "наши данные vs HEMIS", кнопки "Принять наши / Принять HEMIS" | — |
| F10.4 | HEMIS badge в карточке сотрудника | Индикатор синхронизации в карточке сотрудника: "Синхронизирован с HEMIS" / "Не привязан" | — |
| F10.5 | Логи синхронизации | Таблица логов: дата, тип (departments/employees/loads), результат (success/partial/error), количество записей | — |

### Критерии приёмки

- [ ] HEMIS OAuth авторизация работает (univer.hemis.uz)
- [ ] Синхронизация подразделений: создание и обновление
- [ ] Синхронизация сотрудников: маппинг по ПИНФЛ
- [ ] Синхронизация учебной нагрузки
- [ ] Конфликты данных определяются и показываются для ручного разрешения
- [ ] Автоматическая ежедневная синхронизация (Celery beat)
- [ ] Error handling: при недоступности HEMIS API — graceful degradation
- [ ] Тесты: mock HEMIS API, sync logic, conflict resolution

---

## Фаза 11: Appraisal + Training

**Scope: M (Medium)**
**Зависимости: Фаза 2**
**Длительность: ~2.5 недели**

### Описание

Модуль оценки эффективности и обучения сотрудников. Циклы аттестации с KPI-индикаторами, оценка сотрудников руководителями и peer-review, программы обучения и повышения квалификации, учёт сертификатов.

### Backend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| B11.1 | Модель AppraisalCycle | name, start_date, end_date, status (planning/active/review/completed), applicable_departments (M2M), applicable_categories (JSONField) | — |
| B11.2 | Модель KPIIndicator | name (JSONField i18n), description, category (academic/administrative/research/service), weight (%), max_score, applicable_to (JSONField) | — |
| B11.3 | Модель EmployeeAppraisal | cycle (FK), employee (FK), reviewer (FK → Employee), status (pending/self_review/manager_review/completed), overall_score, comments, reviewed_at | B11.1 |
| B11.4 | Модель AppraisalScore | appraisal (FK), kpi (FK), self_score, manager_score, final_score, comment | B11.2, B11.3 |
| B11.5 | Scoring service | AppraisalCalculator: calculate_weighted_score(appraisal) — взвешенный расчёт по KPI, категоризация (Отлично/Хорошо/Удовлетворительно/Неудовлетворительно) | B11.4 |
| B11.6 | Модель TrainingProgram | name (JSONField i18n), description, provider, training_type (internal/external/online), duration_hours, cost, status (planned/active/completed) | — |
| B11.7 | Модель TrainingRecord | employee (FK), program (FK), start_date, end_date, status (enrolled/in_progress/completed/cancelled), certificate_number, certificate_file (FileField), score | B11.6 |
| B11.8 | API endpoints | AppraisalCycleViewSet, KPIIndicatorViewSet, EmployeeAppraisalViewSet (self_review, manager_review, complete), TrainingProgramViewSet, TrainingRecordViewSet | B11.1–B11.7 |
| B11.9 | Appraisal reports | Celery task: генерация сводного отчёта по аттестации (по подразделениям, категориям) | B11.3 |

### Frontend задачи

| # | Задача | Описание | Зависимости |
|---|--------|---------|-------------|
| F11.1 | Циклы аттестации | Страница `/appraisal/cycles`: список циклов, создание, управление статусом | — |
| F11.2 | KPI-индикаторы | Страница `/appraisal/kpis`: справочник KPI, CRUD, распределение весов | — |
| F11.3 | Моя аттестация (Employee) | Страница `/my/appraisal`: самооценка по KPI, просмотр оценки руководителя, итоговый балл | — |
| F11.4 | Оценка подчинённых (Manager) | Страница `/appraisal/review`: список сотрудников для оценки, форма оценки по KPI, комментарии | — |
| F11.5 | Результаты аттестации | Страница `/appraisal/results`: сводная таблица по подразделению, рейтинг, распределение оценок (pie chart) | — |
| F11.6 | Программы обучения | Страница `/training/programs`: каталог программ, регистрация, статус | — |
| F11.7 | Мои курсы (Employee) | Страница `/my/training`: записанные программы, прогресс, сертификаты | — |
| F11.8 | Сертификаты в карточке сотрудника | Таб "Обучение и аттестация": пройденные курсы, сертификаты, история аттестаций | — |
| F11.9 | TanStack Query хуки | useAppraisalCycles(), useMyAppraisal(), useTrainingPrograms(), useTrainingRecords() | — |

### Критерии приёмки

- [ ] Цикл аттестации: создание → самооценка → оценка руководителя → завершение
- [ ] KPI с весами, расчёт взвешенного балла
- [ ] Самооценка и оценка руководителя по каждому KPI
- [ ] Категоризация результата (Отлично/Хорошо/Удовлетворительно/Неудовлетворительно)
- [ ] CRUD программ обучения
- [ ] Регистрация на программу, отслеживание прогресса
- [ ] Upload сертификатов
- [ ] Сводный отчёт по аттестации (по подразделениям)
- [ ] Тесты: scoring calculation, workflow transitions

---

## Сводная таблица

| Фаза | Название | Scope | Зависимости | Backend | Frontend | Длительность |
|------|----------|-------|-------------|---------|----------|-------------|
| 0 | Инфраструктура | L | — | 9 задач | 9 задач | ~3 недели |
| 1 | Auth + RBAC | L | 0 | 9 задач | 9 задач | ~3 недели |
| 2 | Departments + Employees | XL | 1 | 11 задач | 11 задач | ~4 недели |
| 3 | Academic Module | M | 2 | 9 задач | 6 задач | ~2.5 недели |
| 4 | Leaves | M | 2 | 9 задач | 6 задач | ~2.5 недели |
| 5 | Attendance | M | 2 | 8 задач | 6 задач | ~2.5 недели |
| 6 | Recruitment | M | 2 | 8 задач | 7 задач | ~2.5 недели |
| 7 | Payroll | XL | 2,3,4,5 | 11 задач | 9 задач | ~4 недели |
| 8 | Notifications + Telegram | L | все | 11 задач | 7 задач | ~3 недели |
| 9 | Documents + Reports | L | 7,8 | 9 задач | 10 задач | ~3 недели |
| 10 | HEMIS Integration | M | 2,3 | 9 задач | 5 задач | ~2.5 недели |
| 11 | Appraisal + Training | M | 2 | 9 задач | 9 задач | ~2.5 недели |
| **Итого** | | | | **112 задач** | **94 задачи** | **~9 месяцев** |

---

## Параллелизация

Максимальная параллелизация возможна после завершения Фазы 2:

```
Команда A (Backend Senior):  Фаза 7 (Payroll) → Фаза 9 (Documents)
Команда B (Backend Mid):     Фаза 3 (Academic) → Фаза 10 (HEMIS)
Команда C (Backend Mid):     Фаза 4 (Leaves) → Фаза 5 (Attendance)
Команда D (Full-stack):      Фаза 6 (Recruitment) → Фаза 11 (Appraisal)
Команда E (Full-stack):      Фаза 8 (Notifications + Telegram)
```

При команде из **3-4 разработчиков** реалистичный срок: **7-9 месяцев**.
При команде из **5-6 разработчиков** с параллелизацией: **5-6 месяцев**.

---

## Риски и митигация

| Риск | Вероятность | Влияние | Митигация |
|------|------------|---------|-----------|
| HEMIS API нестабилен | Высокая | Среднее | Retry logic, fallback на ручной ввод, кеширование |
| Изменение налогового законодательства | Средняя | Высокое | Конфигурируемые ставки налогов, отдельный settings модуль |
| Сложность расчёта зарплаты | Средняя | Высокое | Поэтапное тестирование, параллельный расчёт с существующей системой |
| Производительность при 2000+ сотрудниках | Низкая | Среднее | Индексы, select_related, пагинация, кеширование |
| Сопротивление пользователей | Средняя | Среднее | Обучение, пошаговый rollout, Telegram Mini App для удобства |
