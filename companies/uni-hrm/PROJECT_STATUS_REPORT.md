# Uni-HRM — Project Status Report

**Дата аудита:** 2026-03-19
**Версия:** 1.0 (post-seed-demo)
**Аудитор:** Claude (автоматический аудит)

---

## 1. Состояние проекта

### Фазы реализации (12/12 ✅)

| Фаза | Описание | Статус |
|------|----------|--------|
| Phase 1 | Django backend setup + DRF | ✅ |
| Phase 2 | Модели данных (Employee, Department, Position) | ✅ |
| Phase 3 | RBAC + Authentication (JWT, Google OAuth) | ✅ |
| Phase 4 | Leaves management | ✅ |
| Phase 5 | Attendance tracking | ✅ |
| Phase 6 | Payroll calculation (UZS, НДФЛ 12%) | ✅ |
| Phase 7 | Recruitment pipeline | ✅ |
| Phase 8 | Appraisal cycles + KPI | ✅ |
| Phase 9 | Training & Development | ✅ |
| Phase 10 | Academic module (нагрузка, степени) | ✅ |
| Phase 11 | Documents & Analytics | ✅ |
| Phase 12 | React SPA + Integrations (HEMIS) | ✅ |

**Дополнительные фазы:**
- Phase 13: Docker + Production deployment ✅
- Phase 14: Frontend Testing (Vitest + Playwright) ✅
- Phase 15: Bundle splitting + lazy loading ✅
- Google OAuth + DevLogin + mock-данные по ролям ✅

---

## 2. Состояние БД (после seed_demo)

### Записи данных

| Модель | Количество | Примечание |
|--------|------------|------------|
| `accounts.User` | 15+ | 7 тестовых + 8 демо |
| `departments.Employee` | **15** | Все активные |
| `departments.Department` | 10 | Ректорат, 3 факультета, 3 кафедры, 3 службы |
| `departments.Position` | 8 | PROF, ASSOC, ASSIST, RECTOR и др. |
| `leaves.LeaveType` | 7 | Annual PPS/AUP/NS, Sick, Maternity, Unpaid, Educational |
| `leaves.LeaveRequest` | **20** | 8 approved, 5 pending, 4 rejected, 3 текущий месяц |
| `attendance.AttendanceRecord` | **204** | Март + Янв-Фев 2026, 6 сотрудников |
| `payroll.TaxConfiguration` | 3 | 2024, 2025, 2026 |
| `payroll.EmployeeSalary` | 15 | Оклады всех сотрудников |
| `payroll.Payroll` | **12** | 6 сотрудников × Янв-Фев 2026 |
| `recruitment.Vacancy` | **2** | Открытые вакансии |
| `recruitment.Candidate` | **5** | Разные стадии pipeline |
| `appraisal.AppraisalCycle` | **1** | 2025-2026 учебный год |
| `appraisal.KPIIndicator` | **5** | Все категории |
| `appraisal.EmployeeAppraisal` | **5** | Разные статусы |
| `appraisal.TrainingProgram` | **2** | Internal + Online |
| `appraisal.TrainingRecord` | **3** | completed/in_progress/enrolled |
| `academic.EmployeeAcademic` | **4** | PhD, DSc + звания |
| `academic.Subject` | **4** | CS101, CS202, AI301, AI201 |
| `academic.AcademicLoad` | **4** | 2025-2026, семестры 1-2 |
| `documents.DocumentTemplate` | 5 | Приказы, договор, справка |
| `notifications.NotificationTemplate` | 4 | Leave, Payslip |

**Итого демо-записей: ~250+**

---

## 3. UI Walkthrough — Результаты

### Тестирование проводилось: роль `hr_manager` (hr@uni-hrm.uz)

| # | Страница | URL | Статус | Данные |
|---|----------|-----|--------|--------|
| 1 | Login | `/login` | ✅ | DevLogin панель |
| 2 | Dashboard | `/dashboard` | ✅ | 15 employees, 204 attendance |
| 3 | Employees | `/employees` | ✅ | 15 сотрудников в таблице |
| 4 | Departments | `/departments` | ✅ | 10 подразделений |
| 5 | Positions | `/positions` | ✅ | 8 должностей |
| 6 | Org Chart | `/org-chart` | ✅ | Дерево структуры |
| 7 | Leaves | `/leaves` | ✅ | 20 заявок |
| 8 | Leave Approval | `/leaves/approval` | ✅ | Pending заявки |
| 9 | Leave Calendar | `/leaves/calendar` | ✅ | Календарь |
| 10 | Attendance | `/attendance` | ✅ | 204 записи |
| 11 | Timesheet | `/timesheet` | ✅ | Табели |
| 12 | Schedules | `/schedules` | ✅ | Рабочие графики |
| 13 | Payroll | `/payroll` | ✅ | 12 расчётных листов |
| 14 | Salary Config | `/salary-config` | ✅ | TaxConfig 2024-2026 |
| 15 | Vacancies | `/recruitment/vacancies` | ✅ | 2 вакансии |
| 16 | Candidates | `/recruitment/candidates` | ✅ | 5 кандидатов |
| 17 | Appraisal Cycles | `/appraisals/cycles` | ✅ | 1 цикл |
| 18 | KPIs | `/appraisals/kpis` | ✅ | 5 показателей |
| 19 | Training Programs | `/training/programs` | ✅ | 2 программы |
| 20 | My Courses | `/training/my-courses` | ✅ | Записи об обучении |
| 21 | Documents | `/documents/templates` | ✅ (исправлено) | 5 шаблонов |
| 22 | Analytics Turnover | `/analytics/turnover` | ✅ | Графики |
| 23 | Notifications | `/notifications` | ✅ | — |
| 24 | Profile | `/profile` | ✅ | Профиль hr@uni-hrm.uz |
| 25 | HR Dashboard | `/dashboard/hr` | ✅ | HR-аналитика |
| 26 | Settings | `/admin/settings` | ✅ | Системные настройки |
| 27 | HEMIS | `/integrations/hemis` | ✅ (исправлено) | Синхронизация |
| 28 | Admin Roles | `/admin/roles` | ⚠️ redirect | Только для super_admin |

**Результат: 27/28 страниц работают (96%). `/admin/roles` — правильный redirect для hr_manager.**

---

## 4. Исправленные баги

### Bug 1: `DocumentTemplatesPage` — `(templates ?? []).map is not a function`
- **Файл:** `frontend/src/features/documents/api.ts`
- **Причина:** API возвращает `{count, results: [...]}` (DRF pagination), компонент ожидал массив
- **Исправление:** `fetchTemplates` теперь извлекает `.results` из пагинированного ответа
- **Статус:** ✅ Исправлено

### Bug 2: `HEMISSyncPage` — `(logs ?? []).slice is not a function`
- **Файл:** `frontend/src/features/hemis/api.ts`
- **Причина:** Аналогично — `fetchSyncLogs` возвращал пагинированный объект
- **Исправление:** Извлечение `.results` при пагинированном ответе
- **Статус:** ✅ Исправлено

### Bug 3: `auth.ts` + `PrivateRoute.tsx` — `Cannot read properties of undefined (reading 'includes')`
- **Файлы:** `frontend/src/store/auth.ts`, `frontend/src/app/PrivateRoute.tsx`
- **Причина:** `user.roles` / `user.permissions` могут быть `undefined` при dev-логине
- **Исправление:** Optional chaining `user?.roles?.includes()`, `user?.permissions?.includes()`
- **Статус:** ✅ Исправлено

---

## 5. Известные проблемы / TODO

### Некритичные (не блокируют работу)

| # | Проблема | Страница | Приоритет |
|---|----------|----------|-----------|
| 1 | WebSocket notification server не запущен (warnings) | все страницы | Low |
| 2 | Google OAuth не работает в localhost (GSI error) | `/login` | Low |
| 3 | i18n ключи не переведены на некоторых страницах (`academic.load`, `academic.references`) | academic | Medium |
| 4 | `/admin/roles` доступен только super_admin — нет страницы "Нет доступа" | admin | Low |
| 5 | Dashboard показывает `Approval: 0` вместо реального числа pending (может быть баг API) | dashboard | Medium |

### Расширения (если нужны)
- Добавить seed_demo данные для конкурсов (PositionContest)
- Заполнить TimeSheet агрегаты из AttendanceRecord
- Добавить генерацию документов (тест `documents/generate`)

---

## 6. Команды для воспроизведения

```bash
# Полный seed с нуля
cd backend
uv run python manage.py seed_all

# Только демо-данные
uv run python manage.py seed_demo

# Проверка данных
uv run python manage.py shell -c "
from apps.departments.models import Employee
from apps.leaves.models import LeaveRequest
from apps.payroll.models import Payroll
from apps.attendance.models import AttendanceRecord
print('Employees:', Employee.objects.count())
print('Leaves:', LeaveRequest.objects.count())
print('Payroll:', Payroll.objects.count())
print('Attendance:', AttendanceRecord.objects.count())
"

# Запуск серверов
uv run python manage.py runserver 8000 &
cd ../frontend && npm run dev &
```

---

## 7. Структура файлов (seed команды)

```
backend/apps/
├── core/management/commands/
│   ├── seed_all.py          # Оркестратор (включает seed_demo)
│   └── seed_demo.py         # ★ НОВЫЙ — реалистичные рабочие данные
├── accounts/management/commands/
│   ├── seed_roles.py        # 7 ролей, 44 permissions
│   └── seed_users.py        # 7 тестовых пользователей
├── departments/management/commands/
│   └── seed_departments.py  # 10 подразделений, 8 должностей
├── leaves/management/commands/
│   └── seed_leaves.py       # 7 типов отпусков, праздники
├── attendance/management/commands/
│   └── seed_attendance.py   # 2 рабочих графика
├── payroll/management/commands/
│   └── seed_payroll.py      # TaxConfig 2024-2025
├── academic/management/commands/
│   └── seed_academic.py     # Степени, звания
├── documents/management/commands/
│   └── seed_documents.py    # 5 шаблонов документов
├── notifications/management/commands/
│   └── seed_notifications.py # 4 шаблона уведомлений
└── settings/management/commands/
    └── seed_settings.py     # Системные настройки
```

---

## 8. Скриншоты

Скриншоты сохранены в `screenshots/` (28 файлов):
- `01-login.png` — Страница входа с DevLogin панелью
- `02-dashboard.png` — Главный дашборд (15 employees, 204 attendance)
- `03-employees.png` — Список сотрудников
- `07-leaves.png` — Заявки на отпуск (20 записей)
- `13-payroll.png` — Расчётные листы (12 записей)
- `15-recruitment-vacancies.png` — Вакансии (2 открытые)
- `17-appraisals-cycles.png` — Цикл аттестации 2025-2026
- `25-dashboard-hr.png` — HR дашборд
- `21-documents-templates.png` — Шаблоны документов (исправлено)
- `27-hemis.png` — HEMIS интеграция (исправлено)
- ... и другие

---

*Отчёт сгенерирован автоматически Claude Code 2026-03-19*
