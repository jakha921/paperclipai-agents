import logging
from typing import Optional

from django.conf import settings

logger = logging.getLogger(__name__)


class HEMISClientError(Exception):
    pass


class HEMISClient:
    """Клиент для работы с HEMIS API."""

    def __init__(self) -> None:
        self.base_url = getattr(settings, "HEMIS_BASE_URL", "https://student.hemis.uz/rest/v1")
        self.token = getattr(settings, "HEMIS_API_TOKEN", "")

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    def _get(self, endpoint: str, params: dict | None = None) -> dict | list:
        """Базовый GET запрос к HEMIS API."""
        if not self.token:
            logger.warning("HEMIS_API_TOKEN not configured, returning mock data")
            return self._get_mock_data(endpoint)

        try:
            import requests

            response = requests.get(
                f"{self.base_url}/{endpoint.lstrip('/')}",
                headers=self.headers,
                params=params or {},
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.error("HEMIS API error for %s: %s", endpoint, exc)
            raise HEMISClientError(str(exc)) from exc

    def _get_mock_data(self, endpoint: str) -> list:
        """Возвращает mock данные когда токен не настроен."""
        mock_data: dict[str, list[dict]] = {
            "departments": [
                {"id": "dept_001", "name": "Кафедра информатики", "code": "CS"},
                {"id": "dept_002", "name": "Кафедра математики", "code": "MATH"},
            ],
            "employees": [
                {
                    "id": "emp_001",
                    "name": "Иванов Иван",
                    "pinfl": "12345678901234",
                    "department_id": "dept_001",
                },
                {
                    "id": "emp_002",
                    "name": "Петрова Мария",
                    "pinfl": "98765432109876",
                    "department_id": "dept_002",
                },
            ],
            "academic-loads": [
                {"id": "load_001", "employee_id": "emp_001", "subject": "Python", "hours": 60},
            ],
        }
        for key, data in mock_data.items():
            if key in endpoint:
                return data
        return []

    def get_departments(self) -> list[dict]:
        """Получить список кафедр/отделов из HEMIS."""
        return self._get("/departments")

    def get_employees(self, department_id: Optional[str] = None) -> list[dict]:
        """Получить список сотрудников из HEMIS."""
        params = {}
        if department_id:
            params["department_id"] = department_id
        return self._get("/employees", params=params)

    def get_academic_loads(self, semester: str) -> list[dict]:
        """Получить учебную нагрузку из HEMIS."""
        return self._get("/academic-loads", params={"semester": semester})
