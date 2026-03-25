# Спецификация интеграций Uni-HRM

> Детальное описание всех внешних интеграций системы управления персоналом университета.
> Документ предназначен для разработчиков и служит руководством к реализации.

---

## Оглавление

1. [Google OAuth 2.0](#1-google-oauth-20)
2. [HEMIS Integration](#2-hemis-integration)
3. [Telegram Gateway API (OTP)](#3-telegram-gateway-api-otp)
4. [Telegram Bot (aiogram 3.x)](#4-telegram-bot-aiogram-3x)
5. [Telegram Mini App](#5-telegram-mini-app)
6. [Email Integration (SMTP)](#6-email-integration-smtp)
7. [Архитектурные диаграммы](#7-архитектурные-диаграммы)

---

## 1. Google OAuth 2.0

### 1.1. Обзор

Google OAuth 2.0 используется как один из методов аутентификации пользователей. Реализация через `django-allauth` (v65+). Пользователь может войти через корпоративный или личный Google-аккаунт. При первом входе создаётся учётная запись `User`, которая впоследствии связывается с `Employee`.

### 1.2. Необходимые scopes

| Scope | Назначение |
|-------|-----------|
| `openid` | Получение ID Token (обязательно для OIDC) |
| `email` | Email-адрес и статус верификации |
| `profile` | Имя, фамилия, аватар |

### 1.3. Переменные окружения

```bash
# .env
GOOGLE_CLIENT_ID=123456789-xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxx
GOOGLE_CALLBACK_URL=https://uni-hrm.example.uz/api/v1/auth/google/callback/
```

### 1.4. Конфигурация django-allauth

```python
# config/settings/base.py

INSTALLED_APPS = [
    # ...
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    # ...
]

MIDDLEWARE = [
    # ...
    "allauth.account.middleware.AccountMiddleware",
    # ...
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# allauth настройки
ACCOUNT_LOGIN_BY_CODE_ENABLED = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "optional"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["openid", "email", "profile"],
        "AUTH_PARAMS": {
            "access_type": "offline",   # Получить refresh token
            "prompt": "consent",        # Всегда показывать consent screen
        },
        "OAUTH_PKCE_ENABLED": True,
        "FETCH_USERINFO": True,
        "APP": {
            "client_id": env("GOOGLE_CLIENT_ID"),
            "secret": env("GOOGLE_CLIENT_SECRET"),
        },
    }
}

# Адаптер для кастомной логики создания пользователя
SOCIALACCOUNT_ADAPTER = "apps.accounts.adapters.CustomSocialAccountAdapter"
ACCOUNT_ADAPTER = "apps.accounts.adapters.CustomAccountAdapter"

# Перенаправление после успешного входа
LOGIN_REDIRECT_URL = "/profile/complete"
ACCOUNT_LOGOUT_REDIRECT_URL = "/login"
```

### 1.5. Кастомные адаптеры

```python
# apps/accounts/adapters.py
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest


class CustomAccountAdapter(DefaultAccountAdapter):
    """Адаптер для управления поведением allauth."""

    def is_open_for_signup(self, request: HttpRequest) -> bool:
        """Регистрация через Google разрешена, прямая -- нет."""
        return False  # Запретить регистрацию по email/password напрямую

    def get_login_redirect_url(self, request: HttpRequest) -> str:
        user = request.user
        if not user.is_profile_completed:
            return "/profile/complete"
        if not user.is_offer_accepted:
            return "/offer/accept"
        if not user.is_approved:
            return "/pending-approval"
        return "/"


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Адаптер для социальной аутентификации."""

    def pre_social_login(self, request: HttpRequest, sociallogin) -> None:
        """
        Привязка Google-аккаунта к существующему пользователю по email.
        Вызывается до создания нового пользователя.
        """
        email = sociallogin.account.extra_data.get("email", "").lower()
        if not email:
            return

        from apps.accounts.models import User

        try:
            existing_user = User.objects.get(email=email)
            # Если пользователь уже есть, но без Google -- привязываем
            if not sociallogin.is_existing:
                sociallogin.connect(request, existing_user)
        except User.DoesNotExist:
            pass  # Будет создан новый пользователь

    def populate_user(self, request: HttpRequest, sociallogin, data: dict) -> "User":
        """Заполнение данных пользователя из Google-профиля."""
        user = super().populate_user(request, sociallogin, data)
        user.first_name = data.get("first_name", "")
        user.last_name = data.get("last_name", "")
        extra = sociallogin.account.extra_data
        user.avatar = extra.get("picture", "")
        user.is_profile_completed = False
        user.is_offer_accepted = False
        user.is_approved = False
        return user

    def is_open_for_signup(self, request: HttpRequest, sociallogin) -> bool:
        """Разрешить регистрацию через Google."""
        return True
```

### 1.6. URL-маршруты

```python
# config/urls.py
urlpatterns = [
    # ...
    path("api/v1/auth/", include("allauth.urls")),
    # Результирующие URL:
    # /api/v1/auth/google/login/          -- инициация OAuth
    # /api/v1/auth/google/login/callback/ -- callback после Google
]
```

### 1.7. Поток аутентификации (пошагово)

```
Шаг 1: Пользователь нажимает "Войти через Google" на фронтенде
        -> Frontend перенаправляет на /api/v1/auth/google/login/

Шаг 2: django-allauth формирует URL авторизации Google:
        https://accounts.google.com/o/oauth2/v2/auth?
          client_id=...&
          redirect_uri=.../callback/&
          scope=openid+email+profile&
          response_type=code&
          access_type=offline&
          prompt=consent&
          state=...&
          code_challenge=...&
          code_challenge_method=S256
        -> Браузер перенаправляется на Google

Шаг 3: Пользователь вводит учётные данные Google, даёт согласие на scopes

Шаг 4: Google перенаправляет на callback URL с authorization code:
        /api/v1/auth/google/login/callback/?code=4/xxx&state=...

Шаг 5: django-allauth обменивает code на токены:
        POST https://oauth2.googleapis.com/token
          grant_type=authorization_code&
          code=4/xxx&
          client_id=...&
          client_secret=...&
          redirect_uri=...&
          code_verifier=...
        -> Ответ: {access_token, refresh_token, id_token, expires_in}

Шаг 6: django-allauth запрашивает профиль пользователя:
        GET https://www.googleapis.com/oauth2/v2/userinfo
          Authorization: Bearer <access_token>
        -> {id, email, verified_email, name, given_name, family_name, picture}

Шаг 7: Вызывается pre_social_login():
        - Если email совпадает с существующим User -> привязка аккаунта
        - Если нет -> вызывается populate_user() -> создание нового User

Шаг 8: django-allauth создаёт Django-сессию, вызывается get_login_redirect_url()

Шаг 9: Backend генерирует JWT (access + refresh) и перенаправляет на фронтенд:
        -> /login/callback?access=<jwt>&refresh=<jwt>

Шаг 10: Frontend сохраняет токены в authStore (Zustand) и localStorage
```

### 1.8. JWT после OAuth

```python
# apps/accounts/views.py
from rest_framework_simplejwt.tokens import RefreshToken


def generate_jwt_for_user(user: "User") -> dict:
    """Генерация JWT-пары для пользователя после OAuth."""
    refresh = RefreshToken.for_user(user)
    refresh["email"] = user.email
    refresh["roles"] = user.get_role_codes()
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
```

### 1.9. Управление токенами Google

| Токен | Назначение | Срок жизни | Хранение |
|-------|-----------|-----------|----------|
| Authorization Code | Обмен на access/refresh | Одноразовый, ~10 мин | Не хранится |
| Google Access Token | Доступ к Google API | 1 час | `SocialToken` (allauth) |
| Google Refresh Token | Обновление access token | Бессрочный (до отзыва) | `SocialToken` (allauth) |
| JWT Access Token | Доступ к Uni-HRM API | 15 мин | localStorage (frontend) |
| JWT Refresh Token | Обновление JWT access | 7 дней | localStorage (frontend) |

### 1.10. Обработка ошибок

| Ошибка | Причина | Действие |
|--------|---------|---------|
| `access_denied` | Пользователь отклонил consent | Перенаправление на `/login?error=consent_denied` |
| `invalid_grant` | Истёк authorization code | Повторная инициация OAuth |
| `network_error` | Нет связи с Google | Показать ошибку, предложить повторить |
| `email_not_verified` | Email не подтверждён в Google | Отклонить вход, показать сообщение |
| `account_inactive` | Пользователь деактивирован в HRM | Показать сообщение "Аккаунт заблокирован" |

```python
# apps/accounts/adapters.py (дополнение)
from allauth.exceptions import ImmediateHttpResponse
from django.http import HttpResponseRedirect


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    # ...

    def authentication_error(
        self, request, provider_id, error=None, exception=None, extra_context=None
    ):
        """Обработка ошибок OAuth."""
        error_code = error or "unknown"
        redirect_url = f"/login?error=oauth_{error_code}"
        return HttpResponseRedirect(redirect_url)
```

### 1.11. Безопасность

- PKCE (Proof Key for Code Exchange) включён для защиты от перехвата authorization code
- `state` параметр генерируется автоматически для защиты от CSRF
- Google Refresh Token хранится в БД (таблица `socialaccount_socialtoken`), зашифрован на уровне приложения
- Callback URL строго зафиксирован в Google Cloud Console
- В production: `ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"`

---

## 2. HEMIS Integration

### 2.1. Обзор

HEMIS (Higher Education Management Information System) -- государственная информационная система Узбекистана для управления высшим образованием. Каждый университет имеет свой поддомен: `univer.hemis.uz` (например, `tuit.hemis.uz`).

Интеграция включает:
- **OAuth 2.0** -- аутентификация сотрудников через HEMIS-аккаунт
- **REST API** -- синхронизация данных: сотрудники, подразделения, нагрузка, степени

### 2.2. Переменные окружения

```bash
# .env
HEMIS_BASE_URL=https://tuit.hemis.uz
HEMIS_API_URL=https://tuit.hemis.uz/rest/v1
HEMIS_CLIENT_ID=uni_hrm_client
HEMIS_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
HEMIS_CALLBACK_URL=https://uni-hrm.example.uz/api/v1/auth/hemis/callback/
HEMIS_API_TOKEN=Bearer xxxxxxxxxxxxxxxxx
HEMIS_SYNC_ENABLED=true
HEMIS_SYNC_BATCH_SIZE=100
```

### 2.3. HEMIS OAuth 2.0

#### Эндпоинты

| Эндпоинт | URL |
|----------|-----|
| Authorization | `{HEMIS_BASE_URL}/oauth/authorize` |
| Token Exchange | `{HEMIS_BASE_URL}/oauth/access-token` |
| User Info | `{HEMIS_API_URL}/auth/me` |
| Revoke Token | `{HEMIS_BASE_URL}/oauth/revoke` |

#### Поток авторизации

```
Шаг 1: Перенаправление на HEMIS
        {HEMIS_BASE_URL}/oauth/authorize?
          response_type=code&
          client_id={HEMIS_CLIENT_ID}&
          redirect_uri={HEMIS_CALLBACK_URL}&
          scope=read&
          state={random_state}

Шаг 2: Пользователь авторизуется в HEMIS

Шаг 3: Callback с authorization code
        GET /api/v1/auth/hemis/callback/?code=xxx&state=xxx

Шаг 4: Обмен code на access token
        POST {HEMIS_BASE_URL}/oauth/access-token
        Content-Type: application/x-www-form-urlencoded
        Body:
          grant_type=authorization_code&
          client_id={HEMIS_CLIENT_ID}&
          client_secret={HEMIS_CLIENT_SECRET}&
          redirect_uri={HEMIS_CALLBACK_URL}&
          code={authorization_code}

        Ответ:
        {
          "access_token": "eyJhbGciOiJIUzI1NiIs...",
          "token_type": "Bearer",
          "expires_in": 86400,
          "refresh_token": "def50200..."
        }

Шаг 5: Получение данных пользователя
        GET {HEMIS_API_URL}/auth/me
        Authorization: Bearer {access_token}

        Ответ:
        {
          "id": "12345",
          "employee_id_number": "EMP-001",
          "name": "Иванов Иван Иванович",
          "login": "i.ivanov",
          "email": "i.ivanov@tuit.uz",
          "role": "teacher",
          "department": {
            "id": "101",
            "name": "Кафедра информатики"
          },
          "faculty": {
            "id": "10",
            "name": "Факультет ИТ"
          }
        }

Шаг 6: Создание/привязка пользователя в Uni-HRM, выдача JWT
```

#### Реализация HEMIS OAuth клиента

```python
# integrations/hemis/oauth.py
import httpx
from django.conf import settings
from django.core.cache import cache


class HEMISOAuthClient:
    """OAuth 2.0 клиент для HEMIS."""

    def __init__(self):
        self.base_url = settings.HEMIS_BASE_URL
        self.api_url = settings.HEMIS_API_URL
        self.client_id = settings.HEMIS_CLIENT_ID
        self.client_secret = settings.HEMIS_CLIENT_SECRET
        self.callback_url = settings.HEMIS_CALLBACK_URL

    def get_authorization_url(self, state: str) -> str:
        """Формирование URL для авторизации в HEMIS."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.callback_url,
            "scope": "read",
            "state": state,
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.base_url}/oauth/authorize?{query}"

    async def exchange_code(self, code: str) -> dict:
        """Обмен authorization code на access token."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/oauth/access-token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.callback_url,
                    "code": code,
                },
            )
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> dict:
        """Получение данных текущего пользователя из HEMIS."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.api_url}/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()

    async def refresh_token(self, refresh_token: str) -> dict:
        """Обновление access token через refresh token."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/oauth/access-token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": refresh_token,
                },
            )
            response.raise_for_status()
            return response.json()
```

### 2.4. HEMIS REST API -- Синхронизация данных

#### API-эндпоинты HEMIS

| Ресурс | Метод | URL | Описание |
|--------|-------|-----|----------|
| Факультеты | GET | `/rest/v1/data/department-list` | Список факультетов |
| Кафедры | GET | `/rest/v1/data/department-list?type=kafedra` | Список кафедр |
| Сотрудники | GET | `/rest/v1/data/employee-list` | Список сотрудников |
| Сотрудник | GET | `/rest/v1/data/employee-info?id={hemis_id}` | Детали сотрудника |
| Предметы | GET | `/rest/v1/data/subject-list` | Список предметов |
| Нагрузка | GET | `/rest/v1/data/employee-subject?employee_id={id}` | Нагрузка сотрудника |
| Степени | GET | `/rest/v1/data/academic-degree-list` | Справочник степеней |
| Звания | GET | `/rest/v1/data/academic-rank-list` | Справочник званий |

Все запросы требуют заголовок `Authorization: Bearer {HEMIS_API_TOKEN}`.

Ответы пагинированы: `?page=1&limit=100`.

#### Примеры запросов и ответов

**Получение списка сотрудников:**

```
GET {HEMIS_API_URL}/data/employee-list?page=1&limit=50
Authorization: Bearer {HEMIS_API_TOKEN}

Ответ:
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "12345",
        "employee_id_number": "EMP-001",
        "first_name": "Иван",
        "second_name": "Иванов",
        "third_name": "Иванович",
        "birth_date": "1985-05-15",
        "gender": {"code": "11", "name": "Мужской"},
        "pinfl": "19850515312345",
        "department": {
          "id": "101",
          "name": "Кафедра информатики",
          "parent": {"id": "10", "name": "Факультет ИТ"}
        },
        "position": {"code": "professor", "name": "Профессор"},
        "academic_degree": {"code": "DSc", "name": "Доктор наук"},
        "academic_rank": {"code": "professor", "name": "Профессор"},
        "employment_form": {"code": "main", "name": "Основное место"},
        "employment_date": "2010-09-01",
        "contract_end_date": "2025-09-01",
        "status": {"code": "active", "name": "Активен"}
      }
    ],
    "pagination": {
      "currentPage": 1,
      "pageCount": 20,
      "totalCount": 987,
      "perPage": 50
    }
  }
}
```

**Получение структуры подразделений:**

```
GET {HEMIS_API_URL}/data/department-list
Authorization: Bearer {HEMIS_API_TOKEN}

Ответ:
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "10",
        "name": "Факультет информационных технологий",
        "code": "FIT",
        "type": {"code": "faculty", "name": "Факультет"},
        "parent_id": null,
        "head": {"id": "999", "name": "Рахимов А.Б."},
        "status": "active"
      },
      {
        "id": "101",
        "name": "Кафедра информатики",
        "code": "KI",
        "type": {"code": "kafedra", "name": "Кафедра"},
        "parent_id": "10",
        "head": {"id": "888", "name": "Каримов С.Д."},
        "status": "active"
      }
    ]
  }
}
```

### 2.5. Маппинг данных

#### Подразделения: HEMIS -> Uni-HRM Department (MPTT)

| Поле HEMIS | Поле Uni-HRM | Трансформация |
|-----------|-------------|---------------|
| `id` | `hemis_id` (новое поле) | Прямое копирование |
| `name` | `name` (JSONField) | `{"ru": hemis.name, "uz": "", "en": ""}` |
| `code` | `code` | Прямое копирование |
| `type.code` | `department_type` | Маппинг: `faculty`->`faculty`, `kafedra`->`department` |
| `parent_id` | `parent` (FK) | Поиск по `hemis_id` родителя |
| `head.id` | `head` (FK) | Поиск Employee по `hemis_id` |
| `status` | `is_active` | `"active"` -> `True`, иначе `False` |

#### Сотрудники: HEMIS -> Uni-HRM Employee

| Поле HEMIS | Поле Uni-HRM | Трансформация |
|-----------|-------------|---------------|
| `id` | `hemis_id` (новое поле) | Прямое копирование |
| `employee_id_number` | `employee_number` | Прямое копирование |
| `first_name` | `user.first_name` | Прямое копирование |
| `second_name` | `user.last_name` | Прямое копирование |
| `third_name` | `user.middle_name` | Прямое копирование |
| `birth_date` | `date_of_birth` | Формат ISO 8601 |
| `gender.code` | `gender` | `"11"` -> `"male"`, `"12"` -> `"female"` |
| `pinfl` | `pinfl` | Прямое копирование (14 цифр) |
| `department.id` | `department` (FK) | Поиск Department по `hemis_id` |
| `position.code` | `position` (FK) | Маппинг кодов должностей |
| `academic_degree.code` | `EmployeeAcademicInfo.degree` | Маппинг: `DSc`->`dsc`, `PhD`->`phd` |
| `academic_rank.code` | `EmployeeAcademicInfo.title` | Маппинг: `professor`->`professor`, `dotsent`->`associate_professor` |
| `employment_form.code` | `employment_type` | Маппинг: `main`->`full_time`, `secondary`->`part_time` |
| `employment_date` | `hire_date` | Формат ISO 8601 |
| `contract_end_date` | `contract_end_date` | Формат ISO 8601 |
| `status.code` | `status` | `"active"` -> `"active"`, `"dismissed"` -> `"terminated"` |

#### Академическая нагрузка: HEMIS -> Uni-HRM AcademicLoad

| Поле HEMIS | Поле Uni-HRM | Трансформация |
|-----------|-------------|---------------|
| `subject.id` | `subject` (FK) | Поиск Subject по `hemis_id` |
| `employee_id` | `employee` (FK) | Поиск Employee по `hemis_id` |
| `academic_year` | `academic_year` | Формат: `"2024-2025"` |
| `semester` | `semester` | 1 или 2 |
| `hours_lecture` | `hours_planned` | Суммирование часов |
| `groups_count` | `groups_count` | Прямое копирование |
| `students_count` | `students_count` | Прямое копирование |

### 2.6. Сервис синхронизации

```python
# integrations/hemis/sync.py
import logging
from typing import Any

import httpx
from django.conf import settings
from django.db import transaction

from apps.departments.models import Department, DepartmentType
from apps.employees.models import Employee

logger = logging.getLogger("hemis.sync")


class HEMISSyncService:
    """Сервис синхронизации данных с HEMIS."""

    def __init__(self):
        self.api_url = settings.HEMIS_API_URL
        self.token = settings.HEMIS_API_TOKEN
        self.batch_size = int(getattr(settings, "HEMIS_SYNC_BATCH_SIZE", 100))
        self.headers = {"Authorization": f"Bearer {self.token}"}

    # ---- HTTP ----

    def _get_paginated(self, endpoint: str, params: dict | None = None) -> list[dict]:
        """Получение всех страниц пагинированного ответа."""
        all_items: list[dict] = []
        page = 1
        params = params or {}

        with httpx.Client(timeout=60) as client:
            while True:
                params.update({"page": page, "limit": self.batch_size})
                response = client.get(
                    f"{self.api_url}/{endpoint}",
                    headers=self.headers,
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

                items = data.get("data", {}).get("items", [])
                all_items.extend(items)

                pagination = data.get("data", {}).get("pagination", {})
                if page >= pagination.get("pageCount", 1):
                    break
                page += 1

        logger.info("HEMIS: получено %d записей из %s", len(all_items), endpoint)
        return all_items

    # ---- Подразделения ----

    @transaction.atomic
    def sync_departments(self) -> dict[str, int]:
        """
        Синхронизация подразделений.
        Стратегия: полная синхронизация (full sync).
        Возвращает: {"created": N, "updated": M, "errors": K}
        """
        items = self._get_paginated("data/department-list")
        stats = {"created": 0, "updated": 0, "errors": 0}

        type_map = {
            "faculty": "faculty",
            "kafedra": "department",
            "otdel": "admin_service",
        }

        # Первый проход: создать/обновить без parent
        for item in items:
            try:
                dept_type_code = type_map.get(
                    item.get("type", {}).get("code", ""), "admin_service"
                )
                dept_type = DepartmentType.objects.get(code=dept_type_code)

                dept, created = Department.objects.update_or_create(
                    hemis_id=item["id"],
                    defaults={
                        "name": {"ru": item["name"], "uz": "", "en": ""},
                        "code": item.get("code", f"HEMIS-{item['id']}"),
                        "department_type": dept_type,
                        "is_active": item.get("status") == "active",
                    },
                )
                stats["created" if created else "updated"] += 1
            except Exception as e:
                logger.error("Ошибка синхронизации подразделения %s: %s", item.get("id"), e)
                stats["errors"] += 1

        # Второй проход: установить parent (MPTT)
        for item in items:
            if item.get("parent_id"):
                try:
                    dept = Department.objects.get(hemis_id=item["id"])
                    parent = Department.objects.get(hemis_id=item["parent_id"])
                    if dept.parent != parent:
                        dept.parent = parent
                        dept.save(update_fields=["parent"])
                except Department.DoesNotExist:
                    logger.warning(
                        "Родитель %s не найден для %s", item["parent_id"], item["id"]
                    )

        Department.objects.rebuild()  # Пересчёт MPTT-дерева
        logger.info("Синхронизация подразделений завершена: %s", stats)
        return stats

    # ---- Сотрудники ----

    @transaction.atomic
    def sync_employees(self) -> dict[str, int]:
        """
        Инкрементальная синхронизация сотрудников.
        Обновляет существующих, создаёт новых.
        Не удаляет записи (soft-delete управляется вручную).
        """
        items = self._get_paginated("data/employee-list")
        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}

        for item in items:
            try:
                self._sync_single_employee(item, stats)
            except Exception as e:
                logger.error("Ошибка синхронизации сотрудника %s: %s", item.get("id"), e)
                stats["errors"] += 1

        logger.info("Синхронизация сотрудников завершена: %s", stats)
        return stats

    def _sync_single_employee(self, item: dict, stats: dict) -> None:
        """Синхронизация одного сотрудника."""
        from apps.accounts.models import User

        hemis_id = item["id"]
        pinfl = item.get("pinfl", "")

        # Поиск существующего сотрудника по hemis_id или pinfl
        employee = None
        if hemis_id:
            employee = Employee.objects.filter(hemis_id=hemis_id).first()
        if not employee and pinfl:
            employee = Employee.objects.filter(pinfl=pinfl).first()

        gender_map = {"11": "male", "12": "female"}
        department = None
        dept_data = item.get("department", {})
        if dept_data and dept_data.get("id"):
            department = Department.objects.filter(hemis_id=dept_data["id"]).first()

        if employee:
            # Обновление существующего сотрудника
            employee.hemis_id = hemis_id
            employee.department = department or employee.department
            employee.date_of_birth = item.get("birth_date") or employee.date_of_birth
            employee.gender = gender_map.get(
                item.get("gender", {}).get("code", ""), employee.gender
            )
            employee.contract_end_date = item.get("contract_end_date")
            employee.save()
            stats["updated"] += 1
        else:
            # Создание нового: сначала User, потом Employee
            email = item.get("email") or f"hemis_{hemis_id}@uni-hrm.local"
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": item.get("first_name", ""),
                    "last_name": item.get("second_name", ""),
                    "middle_name": item.get("third_name", ""),
                    "is_profile_completed": False,
                },
            )
            Employee.objects.create(
                user=user,
                hemis_id=hemis_id,
                employee_number=item.get("employee_id_number", f"H-{hemis_id}"),
                department=department,
                pinfl=pinfl,
                date_of_birth=item.get("birth_date"),
                gender=gender_map.get(item.get("gender", {}).get("code", ""), ""),
                hire_date=item.get("employment_date"),
                contract_end_date=item.get("contract_end_date"),
                status="active",
            )
            stats["created"] += 1

    # ---- Академическая нагрузка ----

    def sync_academic_load(self, academic_year: str) -> dict[str, int]:
        """Синхронизация учебной нагрузки за учебный год."""
        items = self._get_paginated(
            "data/employee-subject", {"academic_year": academic_year}
        )
        stats = {"created": 0, "updated": 0, "errors": 0}

        from apps.academic.models import AcademicLoad, Subject

        for item in items:
            try:
                employee = Employee.objects.filter(
                    hemis_id=item.get("employee_id")
                ).first()
                subject = Subject.objects.filter(
                    hemis_id=item.get("subject", {}).get("id")
                ).first()

                if not employee or not subject:
                    stats["errors"] += 1
                    continue

                _, created = AcademicLoad.objects.update_or_create(
                    employee=employee,
                    subject=subject,
                    academic_year=academic_year,
                    semester=item.get("semester", 1),
                    defaults={
                        "hours_planned": item.get("hours_total", 0),
                        "groups_count": item.get("groups_count", 0),
                        "students_count": item.get("students_count", 0),
                    },
                )
                stats["created" if created else "updated"] += 1
            except Exception as e:
                logger.error("Ошибка синхронизации нагрузки: %s", e)
                stats["errors"] += 1

        return stats
```

### 2.7. Конфликты и стратегия разрешения

| Ситуация | Стратегия |
|----------|----------|
| Поле изменено и в HEMIS, и в Uni-HRM | HEMIS имеет приоритет для: ФИО, подразделение, должность, степень. Uni-HRM имеет приоритет для: контактные данные, адрес, паспорт |
| Сотрудник удалён в HEMIS | НЕ удалять из Uni-HRM; поставить флаг `hemis_sync_status = "removed_in_hemis"` и уведомить HR |
| Новый сотрудник в HEMIS | Создать Employee с минимальными данными, `is_profile_completed = False` |
| Подразделение удалено в HEMIS | Деактивировать (`is_active = False`), не удалять. Сотрудников не перемещать автоматически |
| Дубликат по ПИНФЛ | Привязать к существующему Employee, обновить `hemis_id` |

### 2.8. Celery-задачи для синхронизации

```python
# integrations/hemis/tasks.py
from celery import shared_task
from django.core.mail import mail_admins

from integrations.hemis.sync import HEMISSyncService


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 минут
    autoretry_for=(Exception,),
    acks_late=True,
)
def sync_hemis_departments(self):
    """Синхронизация подразделений с HEMIS. Запуск: ежедневно в 01:00."""
    service = HEMISSyncService()
    stats = service.sync_departments()

    if stats["errors"] > 0:
        mail_admins(
            subject="[Uni-HRM] Ошибки синхронизации подразделений HEMIS",
            message=f"Статистика: {stats}",
        )
    return stats


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=300,
    autoretry_for=(Exception,),
    acks_late=True,
)
def sync_hemis_employees(self):
    """Синхронизация сотрудников с HEMIS. Запуск: ежедневно в 02:00."""
    service = HEMISSyncService()
    stats = service.sync_employees()

    if stats["errors"] > 0:
        mail_admins(
            subject="[Uni-HRM] Ошибки синхронизации сотрудников HEMIS",
            message=f"Статистика: {stats}",
        )
    return stats


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def sync_hemis_academic_load(self, academic_year: str):
    """Синхронизация учебной нагрузки. Запуск: по запросу или раз в неделю."""
    service = HEMISSyncService()
    return service.sync_academic_load(academic_year)
```

```python
# config/celery.py (beat schedule)
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "hemis-sync-departments": {
        "task": "integrations.hemis.tasks.sync_hemis_departments",
        "schedule": crontab(hour=1, minute=0),  # Ежедневно в 01:00 UZT
    },
    "hemis-sync-employees": {
        "task": "integrations.hemis.tasks.sync_hemis_employees",
        "schedule": crontab(hour=2, minute=0),  # Ежедневно в 02:00 UZT
    },
    "hemis-sync-academic-load": {
        "task": "integrations.hemis.tasks.sync_hemis_academic_load",
        "schedule": crontab(hour=3, minute=0, day_of_week=1),  # Понедельник в 03:00
        "args": ("2024-2025",),  # Текущий учебный год (обновляется в настройках)
    },
}
```

### 2.9. Ручная синхронизация через Admin

```python
# integrations/hemis/admin.py
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from unfold.admin import ModelAdmin


@admin.register(HEMISSyncLog)
class HEMISSyncLogAdmin(ModelAdmin):
    list_display = ["sync_type", "status", "created", "updated", "errors", "started_at"]
    change_list_template = "admin/hemis_sync_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "sync-departments/",
                self.sync_departments,
                name="hemis-sync-departments",
            ),
            path(
                "sync-employees/",
                self.sync_employees,
                name="hemis-sync-employees",
            ),
        ]
        return custom_urls + urls

    def sync_departments(self, request):
        from integrations.hemis.tasks import sync_hemis_departments
        sync_hemis_departments.delay()
        self.message_user(request, "Синхронизация подразделений запущена в фоне.")
        return HttpResponseRedirect(reverse("admin:hemis_synclog_changelist"))

    def sync_employees(self, request):
        from integrations.hemis.tasks import sync_hemis_employees
        sync_hemis_employees.delay()
        self.message_user(request, "Синхронизация сотрудников запущена в фоне.")
        return HttpResponseRedirect(reverse("admin:hemis_synclog_changelist"))
```

### 2.10. Модель лога синхронизации

```python
# integrations/hemis/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class HEMISSyncLog(TimestampedModel):
    """Лог синхронизации с HEMIS."""

    class SyncType(models.TextChoices):
        DEPARTMENTS = "departments", _("Подразделения")
        EMPLOYEES = "employees", _("Сотрудники")
        ACADEMIC_LOAD = "academic_load", _("Учебная нагрузка")

    class Status(models.TextChoices):
        STARTED = "started", _("Запущена")
        SUCCESS = "success", _("Успешно")
        PARTIAL = "partial", _("Частично")
        FAILED = "failed", _("Ошибка")

    sync_type = models.CharField(max_length=20, choices=SyncType.choices)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.STARTED
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created = models.IntegerField(default=0, verbose_name=_("Создано"))
    updated = models.IntegerField(default=0, verbose_name=_("Обновлено"))
    errors = models.IntegerField(default=0, verbose_name=_("Ошибки"))
    error_details = models.JSONField(default=list, blank=True)
    triggered_by = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("Лог синхронизации HEMIS")
        verbose_name_plural = _("Логи синхронизации HEMIS")
        ordering = ["-started_at"]
```

### 2.11. Обработка ошибок HEMIS

| Код ответа | Ситуация | Действие |
|-----------|----------|---------|
| 200 | Успех | Обработать данные |
| 401 | Невалидный/просроченный токен | Обновить токен, повторить запрос |
| 403 | Нет доступа | Уведомить администратора, записать в лог |
| 404 | Ресурс не найден | Пропустить запись, записать в лог |
| 429 | Rate limit exceeded | Exponential backoff: 30s, 60s, 120s |
| 500 | Ошибка сервера HEMIS | Retry через 5 минут (max 3 попытки) |
| Timeout | Нет ответа > 60s | Retry через 5 минут |

```python
# integrations/hemis/retry.py
import time
import httpx
import logging

logger = logging.getLogger("hemis.retry")


def request_with_retry(
    method: str,
    url: str,
    headers: dict,
    max_retries: int = 3,
    **kwargs,
) -> httpx.Response:
    """HTTP-запрос с exponential backoff."""
    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=60) as client:
                response = client.request(method, url, headers=headers, **kwargs)

                if response.status_code == 429:
                    wait = min(30 * (2 ** attempt), 300)
                    logger.warning("Rate limit HEMIS, ожидание %ds", wait)
                    time.sleep(wait)
                    continue

                response.raise_for_status()
                return response

        except httpx.TimeoutException:
            logger.warning("Таймаут HEMIS (попытка %d/%d)", attempt + 1, max_retries)
            if attempt < max_retries - 1:
                time.sleep(30 * (2 ** attempt))
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                logger.warning("Ошибка сервера HEMIS %d", e.response.status_code)
                if attempt < max_retries - 1:
                    time.sleep(30 * (2 ** attempt))
                    continue
            raise

    raise httpx.TimeoutException("Превышено число попыток подключения к HEMIS")
```

---

## 3. Telegram Gateway API (OTP)

### 3.1. Обзор

Telegram Gateway API -- официальный сервис Telegram для отправки верификационных кодов. Используется для OTP-аутентификации сотрудников, у которых привязан Telegram-аккаунт. Стоимость: $0.01 за один отправленный код.

Документация: https://core.telegram.org/gateway

### 3.2. Переменные окружения

```bash
# .env
TELEGRAM_GATEWAY_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TELEGRAM_OTP_LENGTH=6
TELEGRAM_OTP_TTL=300          # 5 минут
TELEGRAM_OTP_MAX_ATTEMPTS=3
TELEGRAM_OTP_COOLDOWN=60      # 60 секунд между запросами
```

### 3.3. Поток OTP-верификации

```
Шаг 1: Пользователь вводит email или номер телефона на странице входа
        -> Frontend отправляет POST /api/v1/auth/otp/request/

Шаг 2: Backend проверяет:
        - Существует ли пользователь с таким email/телефоном
        - Привязан ли Telegram (telegram_id != null)
        - Не превышен ли rate limit (1 запрос в 60 сек)
        - Нет ли активного неиспользованного кода

Шаг 3: Backend генерирует 6-значный код, сохраняет в OTPCode с expires_at

Шаг 4: Backend отправляет код через Telegram Gateway API:
        POST https://gatewayapi.telegram.org/sendVerificationMessage
        -> Пользователь получает код в Telegram

Шаг 5: Пользователь вводит код на фронтенде
        -> Frontend отправляет POST /api/v1/auth/otp/verify/

Шаг 6: Backend проверяет:
        - Код совпадает
        - Не истёк (< 5 мин)
        - Не использован
        - Количество попыток < 3

Шаг 7: При успешной проверке:
        - Код помечается как is_used=True
        - Генерируется JWT-пара (access + refresh)
        - Возвращается 200 + токены + user info
```

### 3.4. Реализация

```python
# integrations/telegram/otp.py
import secrets
import logging
from datetime import timedelta

import httpx
from django.conf import settings
from django.utils import timezone

from apps.accounts.models import OTPCode, User

logger = logging.getLogger("telegram.otp")

GATEWAY_URL = "https://gatewayapi.telegram.org"


class TelegramOTPService:
    """Сервис OTP-верификации через Telegram Gateway API."""

    def __init__(self):
        self.token = settings.TELEGRAM_GATEWAY_TOKEN
        self.code_length = int(getattr(settings, "TELEGRAM_OTP_LENGTH", 6))
        self.ttl = int(getattr(settings, "TELEGRAM_OTP_TTL", 300))
        self.max_attempts = int(getattr(settings, "TELEGRAM_OTP_MAX_ATTEMPTS", 3))
        self.cooldown = int(getattr(settings, "TELEGRAM_OTP_COOLDOWN", 60))

    def _generate_code(self) -> str:
        """Генерация криптографически стойкого N-значного кода."""
        return "".join(secrets.choice("0123456789") for _ in range(self.code_length))

    def request_otp(self, user: User) -> dict:
        """
        Запрос OTP для пользователя.
        Возвращает: {"success": True/False, "message": "...", "request_id": "..."}
        """
        if not user.phone:
            return {"success": False, "message": "Номер телефона не привязан"}

        # Проверка cooldown
        recent = OTPCode.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(seconds=self.cooldown),
        ).exists()
        if recent:
            return {
                "success": False,
                "message": f"Подождите {self.cooldown} секунд перед повторным запросом",
            }

        # Инвалидация старых кодов
        OTPCode.objects.filter(user=user, is_used=False).update(is_used=True)

        # Генерация нового кода
        code = self._generate_code()
        otp = OTPCode.objects.create(
            user=user,
            code=code,
            channel="telegram_gateway",
            expires_at=timezone.now() + timedelta(seconds=self.ttl),
        )

        # Отправка через Telegram Gateway API
        result = self._send_via_gateway(user.phone, code)

        if not result["success"]:
            otp.delete()
            return result

        otp.gateway_request_id = result.get("request_id")
        otp.save(update_fields=["gateway_request_id"])

        return {
            "success": True,
            "message": "Код отправлен в Telegram",
            "expires_in": self.ttl,
        }

    def _send_via_gateway(self, phone: str, code: str) -> dict:
        """
        Отправка верификационного сообщения через Telegram Gateway API.

        POST https://gatewayapi.telegram.org/sendVerificationMessage
        {
          "phone_number": "+998901234567",
          "code_length": 6,
          "callback_url": "https://uni-hrm.example.uz/api/v1/webhooks/tg-gateway/",
          "sender_username": "UniHRMBot",
          "code": "123456",
          "ttl": 300
        }
        """
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(
                    f"{GATEWAY_URL}/sendVerificationMessage",
                    headers={"Authorization": f"Bearer {self.token}"},
                    json={
                        "phone_number": phone,
                        "code_length": self.code_length,
                        "code": code,
                        "ttl": self.ttl,
                        "sender_username": "UniHRMBot",
                    },
                )

                data = response.json()

                if not data.get("ok"):
                    logger.error("Telegram Gateway error: %s", data)
                    return {
                        "success": False,
                        "message": "Ошибка отправки кода. Попробуйте позже.",
                    }

                return {
                    "success": True,
                    "request_id": data.get("result", {}).get("request_id"),
                }

        except httpx.TimeoutException:
            logger.error("Telegram Gateway timeout")
            return {"success": False, "message": "Сервис временно недоступен"}
        except Exception as e:
            logger.error("Telegram Gateway exception: %s", e)
            return {"success": False, "message": "Внутренняя ошибка"}

    def verify_otp(self, user: User, code: str) -> dict:
        """
        Проверка OTP-кода.
        Возвращает: {"success": True/False, "message": "..."}
        """
        otp = (
            OTPCode.objects.filter(
                user=user,
                is_used=False,
                channel="telegram_gateway",
            )
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return {"success": False, "message": "Код не найден. Запросите новый."}

        # Проверка истечения
        if timezone.now() > otp.expires_at:
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            return {"success": False, "message": "Код истёк. Запросите новый."}

        # Проверка количества попыток
        if otp.attempts >= self.max_attempts:
            otp.is_used = True
            otp.save(update_fields=["is_used"])
            return {
                "success": False,
                "message": "Превышено число попыток. Запросите новый код.",
            }

        # Проверка кода
        if otp.code != code:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            remaining = self.max_attempts - otp.attempts
            return {
                "success": False,
                "message": f"Неверный код. Осталось попыток: {remaining}",
            }

        # Успех
        otp.is_used = True
        otp.save(update_fields=["is_used"])

        return {"success": True, "message": "Код подтверждён"}
```

### 3.5. API-эндпоинты

```python
# apps/accounts/views.py
from rest_framework import status
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from integrations.telegram.otp import TelegramOTPService


class OTPRateThrottle(AnonRateThrottle):
    rate = "3/minute"


@api_view(["POST"])
@throttle_classes([OTPRateThrottle])
def request_otp(request: Request) -> Response:
    """
    POST /api/v1/auth/otp/request/
    Body: {"email": "user@example.com"} или {"phone": "+998901234567"}
    """
    email = request.data.get("email")
    phone = request.data.get("phone")

    if not email and not phone:
        return Response(
            {"error": "Укажите email или телефон"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from apps.accounts.models import User

    try:
        if email:
            user = User.objects.get(email=email, is_active=True)
        else:
            user = User.objects.get(phone=phone, is_active=True)
    except User.DoesNotExist:
        # Не раскрываем существование пользователя
        return Response({"message": "Если аккаунт существует, код будет отправлен"})

    service = TelegramOTPService()
    result = service.request_otp(user)
    http_status = (
        status.HTTP_200_OK if result["success"] else status.HTTP_429_TOO_MANY_REQUESTS
    )
    return Response(result, status=http_status)


@api_view(["POST"])
@throttle_classes([OTPRateThrottle])
def verify_otp(request: Request) -> Response:
    """
    POST /api/v1/auth/otp/verify/
    Body: {"email": "user@example.com", "code": "123456"}
    """
    email = request.data.get("email")
    phone = request.data.get("phone")
    code = request.data.get("code", "")

    if (not email and not phone) or not code:
        return Response(
            {"error": "Укажите email/телефон и код"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from apps.accounts.models import User

    try:
        if email:
            user = User.objects.get(email=email, is_active=True)
        else:
            user = User.objects.get(phone=phone, is_active=True)
    except User.DoesNotExist:
        return Response(
            {"error": "Неверные данные"}, status=status.HTTP_400_BAD_REQUEST
        )

    service = TelegramOTPService()
    result = service.verify_otp(user, code)

    if not result["success"]:
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    # Генерация JWT
    refresh = RefreshToken.for_user(user)
    return Response({
        "success": True,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": user.get_role_codes(),
        },
    })
```

### 3.6. Безопасность OTP

| Мера | Описание |
|------|---------|
| Криптографическая генерация | `secrets.choice()` вместо `random.randint()` |
| Ограничение попыток | Максимум 3 попытки ввода на один код |
| TTL | Код живёт 5 минут (300 секунд) |
| Cooldown | Минимум 60 секунд между запросами нового кода |
| Rate limiting (IP) | 3 запроса в минуту на IP-адрес |
| Инвалидация | Старые коды инвалидируются при генерации нового |
| Не раскрывать email | При запросе OTP не сообщать, существует ли аккаунт |
| Хеширование кода | В production: хранить `hash(code)`, сравнивать хеши |

---

## 4. Telegram Bot (aiogram 3.x)

### 4.1. Обзор

Telegram-бот предоставляет руководителям и сотрудникам быстрый доступ к ключевым HR-функциям. Реализация на aiogram 3.x с интеграцией в Django через webhook.

### 4.2. Переменные окружения

```bash
# .env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_BOT_WEBHOOK_URL=https://uni-hrm.example.uz/api/v1/webhooks/telegram/
TELEGRAM_BOT_WEBHOOK_SECRET=random_secret_string_for_webhook
TELEGRAM_BOT_ADMIN_IDS=123456789,987654321
```

### 4.3. Архитектура: Webhook

Для production используется webhook-режим (вместо polling), так как:
- Сервер уже работает 24/7 (Django + Nginx)
- Webhook имеет меньшую задержку
- Не требует отдельного long-running процесса

```
┌──────────┐   HTTPS POST    ┌──────────┐   Django view    ┌──────────────┐
│ Telegram │ ────────────────>│  Nginx   │ ────────────────>│  Django      │
│ Servers  │                  │  :443    │                   │  webhook     │
└──────────┘                  └──────────┘                   │  handler     │
                                                             └──────┬───────┘
                                                                    │
                                                             ┌──────v───────┐
                                                             │  aiogram     │
                                                             │  dispatcher  │
                                                             └──────────────┘
```

### 4.4. Настройка webhook

```python
# integrations/telegram/bot.py
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from django.conf import settings

bot = Bot(
    token=settings.TELEGRAM_BOT_TOKEN,
    default_bot_properties={"parse_mode": ParseMode.HTML},
)
dp = Dispatcher()


async def setup_webhook():
    """Установка webhook при старте приложения."""
    webhook_url = settings.TELEGRAM_BOT_WEBHOOK_URL
    secret = settings.TELEGRAM_BOT_WEBHOOK_SECRET
    await bot.set_webhook(
        url=webhook_url,
        secret_token=secret,
        allowed_updates=["message", "callback_query"],
    )
```

```python
# integrations/telegram/views.py
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from aiogram.types import Update

from integrations.telegram.bot import bot, dp


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """
    POST /api/v1/webhooks/telegram/
    Обрабатывает входящие обновления от Telegram.
    """
    # Проверка секрета
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != settings.TELEGRAM_BOT_WEBHOOK_SECRET:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        data = json.loads(request.body)
        update = Update.model_validate(data, context={"bot": bot})
        # Асинхронная обработка через dispatcher
        import asyncio
        loop = asyncio.new_event_loop()
        loop.run_until_complete(dp.feed_update(bot, update))
        loop.close()
    except Exception:
        pass  # Telegram ожидает 200 OK в любом случае

    return JsonResponse({"ok": True})
```

### 4.5. Команды бота

#### /start -- привязка аккаунта (Deep Linking)

```python
# integrations/telegram/handlers/start.py
from aiogram import Router, types
from aiogram.filters import CommandStart, CommandObject

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, command: CommandObject):
    """
    /start -- приветствие
    /start link_<uuid> -- привязка Telegram к аккаунту Uni-HRM

    Deep Link формат:
    https://t.me/UniHRMBot?start=link_550e8400-e29b-41d4-a716-446655440000
    """
    if command.args and command.args.startswith("link_"):
        user_uuid = command.args.replace("link_", "")
        await _link_account(message, user_uuid)
        return

    await message.answer(
        "<b>Uni-HRM Bot</b>\n\n"
        "Доступные команды:\n"
        "/status -- мой статус\n"
        "/leaves -- мои отпуска\n"
        "/help -- помощь\n\n"
        "Для привязки аккаунта используйте ссылку из личного кабинета Uni-HRM."
    )


async def _link_account(message: types.Message, user_uuid: str):
    """Привязка Telegram-аккаунта к пользователю Uni-HRM."""
    from apps.accounts.models import User

    try:
        user = await User.objects.aget(id=user_uuid)
        user.telegram_id = message.from_user.id
        user.telegram_username = message.from_user.username or ""
        await user.asave(update_fields=["telegram_id", "telegram_username"])

        await message.answer(
            f"Аккаунт привязан!\n"
            f"Пользователь: {user.first_name} {user.last_name}\n"
            f"Теперь вы будете получать уведомления в Telegram."
        )
    except User.DoesNotExist:
        await message.answer(
            "Ссылка недействительна. Попробуйте заново из личного кабинета."
        )
```

#### /status -- информация о сотруднике

```python
# integrations/telegram/handlers/status.py
from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("status"))
async def cmd_status(message: types.Message):
    """Показать краткую информацию о сотруднике."""
    from apps.accounts.models import User
    from apps.employees.models import Employee

    try:
        user = await User.objects.aget(telegram_id=message.from_user.id)
        employee = await Employee.objects.select_related(
            "department", "position"
        ).aget(user=user)

        dept_name = (
            employee.department.name.get("ru", "")
            if employee.department
            else "---"
        )
        pos_name = (
            employee.position.name.get("ru", "")
            if employee.position
            else "---"
        )

        await message.answer(
            f"<b>{user.last_name} {user.first_name}</b>\n\n"
            f"Подразделение: {dept_name}\n"
            f"Должность: {pos_name}\n"
            f"Табельный номер: {employee.employee_number}\n"
            f"Статус: {'Активен' if employee.status == 'active' else employee.status}"
        )
    except (User.DoesNotExist, Employee.DoesNotExist):
        await message.answer(
            "Аккаунт не привязан. Используйте ссылку из личного кабинета Uni-HRM."
        )
```

#### /leaves -- баланс отпусков

```python
# integrations/telegram/handlers/leaves.py
from aiogram import Router, types
from aiogram.filters import Command

router = Router()


@router.message(Command("leaves"))
async def cmd_leaves(message: types.Message):
    """Показать баланс отпусков."""
    from apps.accounts.models import User
    from apps.employees.models import Employee
    from apps.leaves.models import LeaveAllocation
    from django.utils import timezone

    try:
        user = await User.objects.aget(telegram_id=message.from_user.id)
        employee = await Employee.objects.aget(user=user)

        allocations = LeaveAllocation.objects.filter(
            employee=employee,
            year=timezone.now().year,
        ).select_related("leave_type")

        lines = ["<b>Баланс отпусков:</b>\n"]
        async for alloc in allocations:
            type_name = alloc.leave_type.name.get("ru", "")
            lines.append(
                f"  {type_name}: {alloc.remaining_days}/{alloc.total_days} дн."
            )

        await message.answer(
            "\n".join(lines) if len(lines) > 1 else "Нет данных об отпусках."
        )
    except (User.DoesNotExist, Employee.DoesNotExist):
        await message.answer("Аккаунт не привязан.")
```

### 4.6. Workflow согласования через inline-кнопки

```python
# integrations/telegram/handlers/approvals.py
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


async def send_leave_approval_request(
    telegram_id: int,
    leave_request_id: str,
    employee_name: str,
    leave_type: str,
    start_date: str,
    end_date: str,
    days: int,
):
    """Отправка запроса на согласование отпуска руководителю."""
    from integrations.telegram.bot import bot

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Одобрить",
                callback_data=f"approve_leave:{leave_request_id}",
            ),
            InlineKeyboardButton(
                text="Отклонить",
                callback_data=f"reject_leave:{leave_request_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="Подробнее",
                url=f"https://uni-hrm.example.uz/leaves/{leave_request_id}",
            ),
        ],
    ])

    await bot.send_message(
        chat_id=telegram_id,
        text=(
            f"<b>Заявка на отпуск</b>\n\n"
            f"Сотрудник: {employee_name}\n"
            f"Тип: {leave_type}\n"
            f"Период: {start_date} -- {end_date}\n"
            f"Дней: {days}\n\n"
            f"Выберите действие:"
        ),
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("approve_leave:"))
async def on_approve_leave(callback: types.CallbackQuery):
    """Обработка нажатия кнопки 'Одобрить'."""
    leave_request_id = callback.data.split(":")[1]

    from apps.accounts.models import User
    from apps.leaves.services import LeaveService

    try:
        user = await User.objects.aget(telegram_id=callback.from_user.id)
        service = LeaveService()
        result = await service.approve(leave_request_id, approved_by=user)

        if result["success"]:
            await callback.message.edit_text(
                callback.message.text + "\n\n<b>ОДОБРЕНО</b>",
                reply_markup=None,
            )
            await callback.answer("Заявка одобрена")
        else:
            await callback.answer(
                f"Ошибка: {result['message']}", show_alert=True
            )
    except User.DoesNotExist:
        await callback.answer("Аккаунт не привязан", show_alert=True)


@router.callback_query(F.data.startswith("reject_leave:"))
async def on_reject_leave(callback: types.CallbackQuery):
    """Обработка нажатия кнопки 'Отклонить'."""
    leave_request_id = callback.data.split(":")[1]

    from apps.accounts.models import User
    from apps.leaves.services import LeaveService

    try:
        user = await User.objects.aget(telegram_id=callback.from_user.id)
        service = LeaveService()
        result = await service.reject(
            leave_request_id,
            rejected_by=user,
            comment="Отклонено через Telegram",
        )

        if result["success"]:
            await callback.message.edit_text(
                callback.message.text + "\n\n<b>ОТКЛОНЕНО</b>",
                reply_markup=None,
            )
            await callback.answer("Заявка отклонена")
        else:
            await callback.answer(
                f"Ошибка: {result['message']}", show_alert=True
            )
    except User.DoesNotExist:
        await callback.answer("Аккаунт не привязан", show_alert=True)
```

### 4.7. Сервис уведомлений

```python
# integrations/telegram/notifications.py
import logging
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from integrations.telegram.bot import bot

logger = logging.getLogger("telegram.notifications")

TEMPLATES = {
    "leave_request_new": {
        "ru": (
            "Новая заявка на отпуск от {employee_name}\n"
            "Тип: {leave_type}\n"
            "Период: {start_date} -- {end_date}"
        ),
        "uz": (
            "{employee_name} dan yangi ta'til arizasi\n"
            "Turi: {leave_type}\n"
            "Davr: {start_date} -- {end_date}"
        ),
        "en": (
            "New leave request from {employee_name}\n"
            "Type: {leave_type}\n"
            "Period: {start_date} -- {end_date}"
        ),
    },
    "leave_approved": {
        "ru": (
            "Ваша заявка на отпуск ({leave_type}) одобрена.\n"
            "Период: {start_date} -- {end_date}"
        ),
        "uz": (
            "Sizning ta'til arizangiz ({leave_type}) tasdiqlandi.\n"
            "Davr: {start_date} -- {end_date}"
        ),
        "en": (
            "Your leave request ({leave_type}) has been approved.\n"
            "Period: {start_date} -- {end_date}"
        ),
    },
    "leave_rejected": {
        "ru": (
            "Ваша заявка на отпуск ({leave_type}) отклонена.\n"
            "Причина: {comment}"
        ),
        "uz": (
            "Sizning ta'til arizangiz ({leave_type}) rad etildi.\n"
            "Sabab: {comment}"
        ),
        "en": (
            "Your leave request ({leave_type}) has been rejected.\n"
            "Reason: {comment}"
        ),
    },
    "contract_expiry": {
        "ru": (
            "Внимание: контракт сотрудника {employee_name} "
            "истекает {expiry_date}. Осталось {days_left} дн."
        ),
        "uz": (
            "Diqqat: {employee_name} shartnomasi {expiry_date} "
            "da tugaydi. {days_left} kun qoldi."
        ),
        "en": (
            "Notice: Contract of {employee_name} expires on "
            "{expiry_date}. {days_left} days left."
        ),
    },
    "payroll_ready": {
        "ru": (
            "Расчёт зарплаты за {month}/{year} завершён.\n"
            "К выплате: {net_salary} сум"
        ),
        "uz": (
            "{month}/{year} oy uchun ish haqi hisoblandi.\n"
            "To'lov: {net_salary} so'm"
        ),
        "en": (
            "Payroll for {month}/{year} is ready.\n"
            "Net salary: {net_salary} UZS"
        ),
    },
}


async def send_notification(
    telegram_id: int,
    template_key: str,
    lang: str = "ru",
    **kwargs,
) -> bool:
    """
    Отправка шаблонного уведомления пользователю.
    Возвращает True при успехе, False при ошибке.
    """
    template = TEMPLATES.get(template_key, {}).get(lang)
    if not template:
        logger.error("Шаблон не найден: %s/%s", template_key, lang)
        return False

    text = template.format(**kwargs)

    try:
        await bot.send_message(chat_id=telegram_id, text=text)
        return True
    except TelegramForbiddenError:
        logger.warning("Пользователь %d заблокировал бота", telegram_id)
        return False
    except TelegramBadRequest as e:
        logger.error("Ошибка отправки Telegram %d: %s", telegram_id, e)
        return False
```

### 4.8. Celery-задачи для уведомлений

```python
# integrations/telegram/tasks.py
import asyncio
from celery import shared_task


@shared_task
def send_telegram_notification(
    telegram_id: int, template_key: str, lang: str = "ru", **kwargs
):
    """Асинхронная отправка Telegram-уведомления через Celery."""
    from integrations.telegram.notifications import send_notification

    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(
        send_notification(telegram_id, template_key, lang, **kwargs)
    )
    loop.close()
    return result


@shared_task
def notify_contract_expiry():
    """Ежедневная проверка истекающих контрактов. Уведомление HR за 30 и 7 дней."""
    from datetime import timedelta
    from django.utils import timezone
    from apps.employees.models import Employee

    today = timezone.now().date()

    for days_before in [30, 7]:
        target_date = today + timedelta(days=days_before)
        employees = Employee.objects.filter(
            contract_end_date=target_date,
            status="active",
        ).select_related("user", "department")

        for emp in employees:
            if emp.user.telegram_id:
                send_telegram_notification.delay(
                    telegram_id=emp.user.telegram_id,
                    template_key="contract_expiry",
                    lang=emp.user.language or "ru",
                    employee_name=f"{emp.user.last_name} {emp.user.first_name}",
                    expiry_date=target_date.strftime("%d.%m.%Y"),
                    days_left=days_before,
                )
```

### 4.9. Регистрация роутеров

```python
# integrations/telegram/bot.py (дополнение)
from integrations.telegram.handlers.start import router as start_router
from integrations.telegram.handlers.status import router as status_router
from integrations.telegram.handlers.leaves import router as leaves_router
from integrations.telegram.handlers.approvals import router as approvals_router

dp.include_router(start_router)
dp.include_router(status_router)
dp.include_router(leaves_router)
dp.include_router(approvals_router)
```

---

## 5. Telegram Mini App

### 5.1. Обзор

Telegram Mini App -- React SPA, запускаемый внутри Telegram через кнопку бота или ссылку. Предоставляет мобильный интерфейс для сотрудников: просмотр профиля, подача заявлений на отпуск, проверка баланса, уведомления.

### 5.2. Архитектура

```
┌────────────────────────────────────────┐
│          Telegram Client               │
│  ┌──────────────────────────────────┐  │
│  │     Telegram WebApp Container    │  │
│  │  ┌────────────────────────────┐  │  │
│  │  │   Mini App (React SPA)     │  │  │
│  │  │   /miniapp/ route          │  │  │
│  │  └────────────┬───────────────┘  │  │
│  └───────────────│──────────────────┘  │
└──────────────────│─────────────────────┘
                   │ HTTPS API calls
                   v
          ┌────────────────┐
          │   Django API   │
          │   /api/v1/...  │
          └────────────────┘
```

Mini App встроен в основной React-проект (frontend), но рендерится в отдельном layout (`MiniAppLayout.tsx`) без сайдбара и хедера. Бандлится как часть основного build, доступен по пути `/miniapp/`.

### 5.3. Аутентификация через initData

Telegram передаёт `initData` при запуске Mini App. Backend валидирует эти данные для аутентификации пользователя.

```
Шаг 1: Пользователь открывает Mini App в Telegram

Шаг 2: Telegram WebApp SDK предоставляет initData:
        Telegram.WebApp.initData -- строка с данными пользователя,
        подписанная HMAC-SHA256 ботовым токеном

Шаг 3: Frontend отправляет initData на backend:
        POST /api/v1/auth/telegram-miniapp/
        Body: {"init_data": "..."}

Шаг 4: Backend валидирует подпись initData:
        - Парсит query string
        - Вычисляет HMAC-SHA256 от data_check_string используя secret_key
        - Сравнивает с полученным hash
        - Проверяет auth_date (не старше 5 минут)

Шаг 5: При успехе:
        - Находит/создаёт User по telegram_id
        - Генерирует JWT
        - Возвращает токены + user info
```

### 5.4. Валидация initData на backend

```python
# integrations/telegram/miniapp.py
import hashlib
import hmac
import json
import time
from urllib.parse import parse_qs, unquote

from django.conf import settings


def validate_init_data(init_data: str, max_age: int = 300) -> dict | None:
    """
    Валидация Telegram Mini App initData.

    Args:
        init_data: Raw initData строка от Telegram.WebApp.initData
        max_age: Максимальный возраст данных в секундах (по умолчанию 5 мин)

    Returns:
        dict с данными пользователя при успешной валидации, None при ошибке
    """
    parsed = parse_qs(init_data)
    received_hash = parsed.get("hash", [None])[0]
    if not received_hash:
        return None

    # Формирование data_check_string
    # Все параметры (кроме hash), отсортированные по ключу, в формате "key=value\n"
    data_parts = []
    for key in sorted(parsed.keys()):
        if key != "hash":
            data_parts.append(f"{key}={unquote(parsed[key][0])}")
    data_check_string = "\n".join(data_parts)

    # Вычисление секретного ключа
    bot_token = settings.TELEGRAM_BOT_TOKEN
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256,
    ).digest()

    # Вычисление хеша
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if calculated_hash != received_hash:
        return None

    # Проверка auth_date
    auth_date = int(parsed.get("auth_date", [0])[0])
    if time.time() - auth_date > max_age:
        return None

    # Парсинг user data
    user_data = parsed.get("user", [None])[0]
    if user_data:
        return json.loads(unquote(user_data))

    return None
```

### 5.5. API-эндпоинт Mini App авторизации

```python
# apps/accounts/views.py

@api_view(["POST"])
def telegram_miniapp_auth(request: Request) -> Response:
    """
    POST /api/v1/auth/telegram-miniapp/
    Body: {"init_data": "query_id=...&user=...&auth_date=...&hash=..."}
    """
    init_data = request.data.get("init_data", "")
    if not init_data:
        return Response({"error": "init_data обязателен"}, status=400)

    from integrations.telegram.miniapp import validate_init_data

    user_data = validate_init_data(init_data)
    if not user_data:
        return Response({"error": "Невалидные данные"}, status=401)

    telegram_id = user_data.get("id")
    if not telegram_id:
        return Response({"error": "telegram_id отсутствует"}, status=400)

    from apps.accounts.models import User

    try:
        user = User.objects.get(telegram_id=telegram_id, is_active=True)
    except User.DoesNotExist:
        return Response(
            {
                "error": (
                    "Аккаунт не привязан к Telegram. "
                    "Привяжите через /start бота."
                )
            },
            status=404,
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": user.get_role_codes(),
        },
    })
```

### 5.6. Frontend Mini App

```tsx
// src/modules/miniapp/MiniAppEntry.tsx
import { useEffect, useState } from "react";
import { apiClient } from "@/shared/api/apiClient";
import { useAuthStore } from "@/store/authStore";

declare global {
  interface Window {
    Telegram: {
      WebApp: {
        initData: string;
        initDataUnsafe: Record<string, unknown>;
        ready: () => void;
        expand: () => void;
        close: () => void;
        colorScheme: "light" | "dark";
        themeParams: Record<string, string>;
        MainButton: {
          text: string;
          show: () => void;
          hide: () => void;
          onClick: (cb: () => void) => void;
        };
      };
    };
  }
}

export function MiniAppEntry() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const setTokens = useAuthStore((s) => s.setTokens);

  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) {
      setError("Приложение доступно только в Telegram");
      setLoading(false);
      return;
    }

    tg.ready();
    tg.expand();

    async function authenticate() {
      try {
        const response = await apiClient.post("/auth/telegram-miniapp/", {
          init_data: tg.initData,
        });
        setTokens(response.data.access, response.data.refresh);
        setLoading(false);
      } catch {
        setError("Ошибка авторизации. Привяжите аккаунт через бота.");
        setLoading(false);
      }
    }

    authenticate();
  }, [setTokens]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        Загрузка...
      </div>
    );
  }
  if (error) return <div className="p-4 text-red-500">{error}</div>;

  return <MiniAppRouter />;
}
```

### 5.7. Адаптация темы

```tsx
// src/modules/miniapp/hooks/useTelegramTheme.ts
import { useEffect } from "react";

export function useTelegramTheme() {
  useEffect(() => {
    const tg = window.Telegram?.WebApp;
    if (!tg) return;

    const root = document.documentElement;
    const params = tg.themeParams;

    // Применение цветов Telegram к CSS-переменным
    if (params.bg_color)
      root.style.setProperty("--tg-bg", params.bg_color);
    if (params.text_color)
      root.style.setProperty("--tg-text", params.text_color);
    if (params.button_color)
      root.style.setProperty("--tg-button", params.button_color);
    if (params.button_text_color)
      root.style.setProperty("--tg-button-text", params.button_text_color);

    // Установка класса темы
    if (tg.colorScheme === "dark") {
      document.body.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
    }
  }, []);
}
```

### 5.8. Функции Mini App

| Экран | Маршрут | Описание |
|-------|---------|---------|
| Профиль | `/miniapp/` | ФИО, должность, подразделение, контакты |
| Отпуска | `/miniapp/leaves` | Баланс, список заявок, кнопка "Подать заявку" |
| Новая заявка | `/miniapp/leaves/new` | Форма: тип, даты, причина |
| Уведомления | `/miniapp/notifications` | Список уведомлений |
| Расчётный лист | `/miniapp/payslip` | Текущий расчётный лист |

### 5.9. Деплой Mini App

Mini App -- часть основного React SPA, доступен по пути `/miniapp/*`.

```python
# Настройка в BotFather
# Через @BotFather > Bot Settings > Menu Button:
# URL: https://uni-hrm.example.uz/miniapp/
```

```nginx
# nginx.conf -- Mini App отдаётся как часть SPA
location /miniapp/ {
    root /app/static/frontend;
    try_files $uri $uri/ /index.html;
}
```

---

## 6. Email Integration (SMTP)

### 6.1. Переменные окружения

```bash
# .env (production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=noreply@university.uz
EMAIL_HOST_PASSWORD=app-specific-password
DEFAULT_FROM_EMAIL="Uni-HRM <noreply@university.uz>"
```

### 6.2. Конфигурация Django

```python
# config/settings/base.py
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL", default="Uni-HRM <noreply@university.uz>"
)

# config/settings/development.py (переопределение для разработки)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

### 6.3. Шаблоны email

```python
# apps/notifications/email.py
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_templated_email(
    to_email: str,
    subject: str,
    template_name: str,
    context: dict,
    from_email: str | None = None,
) -> bool:
    """Отправка email по HTML-шаблону."""
    html_content = render_to_string(f"emails/{template_name}.html", context)
    text_content = render_to_string(f"emails/{template_name}.txt", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email or settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send(fail_silently=False)
        return True
    except Exception:
        return False
```

### 6.4. Типы email-уведомлений

| Шаблон | Триггер | Получатель |
|--------|---------|-----------|
| `invite.html` | HR создал сотрудника | Новый сотрудник |
| `password_reset.html` | Запрос сброса пароля | Пользователь |
| `leave_request.html` | Новая заявка на отпуск | Руководитель |
| `leave_approved.html` | Заявка одобрена | Сотрудник |
| `leave_rejected.html` | Заявка отклонена | Сотрудник |
| `payroll_ready.html` | Расчёт зарплаты завершён | Сотрудник |
| `contract_expiry.html` | Контракт истекает через 30/7 дней | HR + сотрудник |

### 6.5. Асинхронная отправка через Celery

```python
# apps/notifications/tasks.py
from celery import shared_task


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
)
def send_email_async(
    self, to_email: str, subject: str, template_name: str, context: dict
):
    """Асинхронная отправка email."""
    from apps.notifications.email import send_templated_email
    return send_templated_email(to_email, subject, template_name, context)
```

---

## 7. Архитектурные диаграммы

### 7.1. Google OAuth Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Browser  │     │ Frontend │     │ Backend  │     │ Google   │
│          │     │ React    │     │ Django   │     │ OAuth    │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                 │
     │ 1. Click       │                │                 │
     │ "Login Google" │                │                 │
     │───────────────>│                │                 │
     │                │ 2. Redirect to │                 │
     │                │ /auth/google/  │                 │
     │                │───────────────>│                 │
     │                │                │ 3. Build auth   │
     │                │                │ URL + state     │
     │<───────────────┼────────────────│                 │
     │   302 Redirect to Google        │                 │
     │                │                │                 │
     │ 4. Login + consent              │                 │
     │─────────────────────────────────┼────────────────>│
     │                │                │                 │
     │<────────────────────────────────┼─────────────────│
     │   5. Redirect with ?code=xxx    │                 │
     │                │                │                 │
     │───────────────>│───────────────>│                 │
     │                │ 6. Callback    │                 │
     │                │                │ 7. Exchange     │
     │                │                │ code for tokens │
     │                │                │────────────────>│
     │                │                │                 │
     │                │                │<────────────────│
     │                │                │ 8. access_token │
     │                │                │    + user info  │
     │                │                │                 │
     │                │                │ 9. Find/create  │
     │                │                │    User + JWT   │
     │                │                │                 │
     │<───────────────┼────────────────│                 │
     │   10. Redirect /login/callback?access=xxx         │
     │                │                │                 │
     │───────────────>│                │                 │
     │                │ 11. Store JWT  │                 │
     │                │ in authStore   │                 │
     │<───────────────│                │                 │
     │   12. Redirect │                │                 │
     │   to dashboard │                │                 │
```

### 7.2. HEMIS Sync Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Celery   │     │ HEMIS    │     │ Django   │     │ Database │
│ Beat     │     │ Sync     │     │ ORM      │     │ Postgres │
│          │     │ Service  │     │          │     │          │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                 │
     │ 1. Trigger     │                │                 │
     │ at 02:00 UZT   │                │                 │
     │───────────────>│                │                 │
     │                │                │                 │
     │                │ 2. GET /rest/v1/data/            │
     │                │    department-list               │
     │                │───────────────>(HEMIS API)       │
     │                │<───────────────                  │
     │                │ 3. JSON response                 │
     │                │                │                 │
     │                │ 4. For each    │                 │
     │                │    department: │                 │
     │                │    update_or_  │                 │
     │                │    create()    │                 │
     │                │───────────────>│                 │
     │                │                │───────────────> │
     │                │                │ 5. INSERT/UPDATE│
     │                │                │<────────────────│
     │                │                │                 │
     │                │ 6. Rebuild     │                 │
     │                │    MPTT tree   │                 │
     │                │───────────────>│                 │
     │                │                │───────────────> │
     │                │                │<────────────────│
     │                │                │                 │
     │                │ 7. GET /rest/v1/data/            │
     │                │    employee-list                 │
     │                │───────────────>(HEMIS API)       │
     │                │<───────────────                  │
     │                │                │                 │
     │                │ 8. For each    │                 │
     │                │    employee:   │                 │
     │                │    sync logic  │                 │
     │                │───────────────>│                 │
     │                │                │───────────────> │
     │                │                │<────────────────│
     │                │                │                 │
     │                │ 9. Log result  │                 │
     │                │    to SyncLog  │                 │
     │                │───────────────>│                 │
     │                │                │───────────────> │
     │<───────────────│                │                 │
     │ 10. Return     │                │                 │
     │     stats      │                │                 │
     │                │                │                 │
     │ 11. If errors: │                │                 │
     │ send email to  │                │                 │
     │ admins         │                │                 │
```

### 7.3. Telegram OTP Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ User     │     │ Frontend │     │ Backend  │     │ Telegram │
│          │     │ React    │     │ Django   │     │ Gateway  │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                 │
     │ 1. Enter email │                │                 │
     │───────────────>│                │                 │
     │                │ 2. POST        │                 │
     │                │ /auth/otp/     │                 │
     │                │ request/       │                 │
     │                │───────────────>│                 │
     │                │                │ 3. Generate     │
     │                │                │    6-digit code │
     │                │                │ 4. Save OTPCode │
     │                │                │                 │
     │                │                │ 5. POST         │
     │                │                │ /sendVerifica-  │
     │                │                │ tionMessage     │
     │                │                │────────────────>│
     │                │                │<────────────────│
     │                │                │ 6. OK           │
     │                │<───────────────│                 │
     │                │ 7. "Код        │                 │
     │<───────────────│    отправлен"  │                 │
     │                │                │                 │
     │ [Telegram msg] │                │                 │
     │<──────────────────────────────────────────────────│
     │ 8. "Ваш код:   │                │                 │
     │     123456"    │                │                 │
     │                │                │                 │
     │ 9. Enter code  │                │                 │
     │───────────────>│                │                 │
     │                │ 10. POST       │                 │
     │                │ /auth/otp/     │                 │
     │                │ verify/        │                 │
     │                │───────────────>│                 │
     │                │                │ 11. Validate:   │
     │                │                │  - code match   │
     │                │                │  - not expired  │
     │                │                │  - attempts < 3 │
     │                │                │                 │
     │                │                │ 12. Generate    │
     │                │                │     JWT pair    │
     │                │<───────────────│                 │
     │                │ 13. {access,   │                 │
     │<───────────────│     refresh,   │                 │
     │ 14. Redirect   │     user}      │                 │
     │ to dashboard   │                │                 │
```

### 7.4. Telegram Bot Approval Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Employee │     │ Backend  │     │ Telegram │     │ Manager  │
│ (Web)    │     │ Django   │     │ Bot      │     │ (Tg App) │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                 │
     │ 1. Submit      │                │                 │
     │ leave request  │                │                 │
     │───────────────>│                │                 │
     │                │ 2. Create      │                 │
     │                │ LeaveRequest   │                 │
     │                │ (pending_head) │                 │
     │                │                │                 │
     │                │ 3. Find        │                 │
     │                │ manager's      │                 │
     │                │ telegram_id    │                 │
     │                │                │                 │
     │                │ 4. Send msg    │                 │
     │                │ with inline    │                 │
     │                │ keyboard       │                 │
     │                │───────────────>│                 │
     │                │                │ 5. Deliver      │
     │                │                │ message         │
     │                │                │────────────────>│
     │                │                │                 │
     │                │                │                 │ 6. Manager
     │                │                │                 │ clicks
     │                │                │                 │ [Одобрить]
     │                │                │<────────────────│
     │                │                │ 7. Callback     │
     │                │                │ query:          │
     │                │                │ approve_leave:  │
     │                │                │ {id}            │
     │                │                │                 │
     │                │<───────────────│                 │
     │                │ 8. Webhook     │                 │
     │                │ handler        │                 │
     │                │                │                 │
     │                │ 9. Update      │                 │
     │                │ LeaveRequest   │                 │
     │                │ -> pending_hr  │                 │
     │                │                │                 │
     │                │ 10. Edit msg:  │                 │
     │                │ "ОДОБРЕНО"     │                 │
     │                │───────────────>│                 │
     │                │                │────────────────>│
     │                │                │                 │
     │                │ 11. Notify     │                 │
     │                │ employee       │                 │
     │<───────────────│ (email/tg)     │                 │
```

### 7.5. Telegram Mini App Auth Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Telegram │     │ Mini App │     │ Backend  │
│ Client   │     │ React    │     │ Django   │
└────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │
     │ 1. User opens  │                │
     │ Mini App via   │                │
     │ bot menu       │                │
     │───────────────>│                │
     │                │                │
     │ 2. Telegram    │                │
     │ injects        │                │
     │ WebApp SDK     │                │
     │ + initData     │                │
     │                │                │
     │                │ 3. Read        │
     │                │ Telegram.      │
     │                │ WebApp.        │
     │                │ initData       │
     │                │                │
     │                │ 4. POST        │
     │                │ /auth/telegram │
     │                │ -miniapp/      │
     │                │ {init_data}    │
     │                │───────────────>│
     │                │                │
     │                │                │ 5. Validate
     │                │                │ HMAC-SHA256
     │                │                │ signature
     │                │                │
     │                │                │ 6. Check
     │                │                │ auth_date
     │                │                │ freshness
     │                │                │
     │                │                │ 7. Find User
     │                │                │ by telegram_id
     │                │                │
     │                │                │ 8. Generate
     │                │                │ JWT pair
     │                │                │
     │                │<───────────────│
     │                │ 9. {access,    │
     │                │  refresh, user}│
     │                │                │
     │                │ 10. Store in   │
     │                │ authStore      │
     │                │                │
     │<───────────────│ 11. Render     │
     │ 12. Show       │ Mini App UI   │
     │ Mini App       │                │
```

---

## Сводная таблица переменных окружения

| Переменная | Описание | Пример |
|-----------|---------|--------|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | `123..apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | `GOCSPX-xxx` |
| `HEMIS_BASE_URL` | Базовый URL HEMIS | `https://tuit.hemis.uz` |
| `HEMIS_API_URL` | API URL HEMIS | `https://tuit.hemis.uz/rest/v1` |
| `HEMIS_CLIENT_ID` | HEMIS OAuth client ID | `uni_hrm_client` |
| `HEMIS_CLIENT_SECRET` | HEMIS OAuth client secret | `xxx` |
| `HEMIS_API_TOKEN` | Токен для REST API HEMIS | `Bearer xxx` |
| `HEMIS_SYNC_ENABLED` | Включить синхронизацию | `true` |
| `HEMIS_SYNC_BATCH_SIZE` | Размер пакета синхронизации | `100` |
| `TELEGRAM_GATEWAY_TOKEN` | Токен Telegram Gateway API | `xxx` |
| `TELEGRAM_OTP_LENGTH` | Длина OTP-кода | `6` |
| `TELEGRAM_OTP_TTL` | Время жизни кода (секунды) | `300` |
| `TELEGRAM_OTP_MAX_ATTEMPTS` | Макс. попыток ввода кода | `3` |
| `TELEGRAM_OTP_COOLDOWN` | Задержка между запросами (сек) | `60` |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram-бота | `123456789:ABCxxx` |
| `TELEGRAM_BOT_WEBHOOK_URL` | URL webhook бота | `https://uni-hrm.../webhooks/telegram/` |
| `TELEGRAM_BOT_WEBHOOK_SECRET` | Секрет для проверки webhook | `random_string` |
| `EMAIL_HOST` | SMTP-сервер | `smtp.gmail.com` |
| `EMAIL_PORT` | Порт SMTP | `587` |
| `EMAIL_USE_TLS` | Использовать TLS | `true` |
| `EMAIL_HOST_USER` | Email для SMTP-аутентификации | `noreply@university.uz` |
| `EMAIL_HOST_PASSWORD` | Пароль SMTP | `app-specific-password` |
| `DEFAULT_FROM_EMAIL` | Адрес отправителя | `Uni-HRM <noreply@university.uz>` |
