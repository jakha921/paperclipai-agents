import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.recruitment.models import Candidate, Vacancy

User = get_user_model()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin_recruit",
        email="admin_recruit@test.com",
        password="testpass123",
    )


@pytest.fixture
def api_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.mark.django_db
class TestVacancyAPI:
    def test_list_vacancies_empty(self, api_client):
        response = api_client.get("/api/v1/recruitment/vacancies/")
        assert response.status_code == 200
        assert response.data["count"] == 0

    def test_create_vacancy(self, api_client, department):
        data = {
            "title": {"ru": "Новая вакансия"},
            "department": str(department.id),
            "vacancies_count": 2,
        }
        response = api_client.post("/api/v1/recruitment/vacancies/", data, format="json")
        assert response.status_code == 201
        assert response.data["id"] is not None

    def test_list_vacancies(self, api_client, department):
        Vacancy.objects.create(title={"ru": "Тест"}, department=department)
        response = api_client.get("/api/v1/recruitment/vacancies/")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_publish_vacancy(self, api_client, department):
        v = Vacancy.objects.create(title={"ru": "Тест"}, department=department)
        response = api_client.post(f"/api/v1/recruitment/vacancies/{v.id}/publish/")
        assert response.status_code == 200
        assert response.data["status"] == "OPEN"
        v.refresh_from_db()
        assert v.status == Vacancy.Status.OPEN

    def test_close_vacancy(self, api_client, department):
        v = Vacancy.objects.create(
            title={"ru": "Тест"}, department=department, status=Vacancy.Status.OPEN
        )
        response = api_client.post(f"/api/v1/recruitment/vacancies/{v.id}/close/")
        assert response.status_code == 200
        assert response.data["status"] == "CLOSED"

    def test_filter_by_status(self, api_client, department):
        Vacancy.objects.create(
            title={"ru": "Открытая"}, department=department, status=Vacancy.Status.OPEN
        )
        Vacancy.objects.create(
            title={"ru": "Черновик"}, department=department, status=Vacancy.Status.DRAFT
        )
        response = api_client.get("/api/v1/recruitment/vacancies/?status=OPEN")
        assert response.status_code == 200
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestCandidateAPI:
    def test_create_candidate(self, api_client, department):
        v = Vacancy.objects.create(title={"ru": "Вакансия"}, department=department)
        data = {
            "vacancy": str(v.id),
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone": "+998901234567",
            "source": "EXTERNAL",
        }
        response = api_client.post("/api/v1/recruitment/candidates/", data, format="json")
        assert response.status_code == 201

    def test_reject_candidate(self, api_client, department):
        v = Vacancy.objects.create(title={"ru": "Вакансия"}, department=department)
        c = Candidate.objects.create(
            vacancy=v,
            first_name="Иван",
            last_name="Иванов",
            phone="+998901234567",
        )
        response = api_client.post(f"/api/v1/recruitment/candidates/{c.id}/reject/")
        assert response.status_code == 200
        assert response.data["stage"] == "REJECTED"
        c.refresh_from_db()
        assert c.stage == Candidate.Stage.REJECTED

    def test_filter_by_stage(self, api_client, department):
        v = Vacancy.objects.create(title={"ru": "Вакансия"}, department=department)
        Candidate.objects.create(
            vacancy=v,
            first_name="Кандидат1",
            last_name="Тест",
            phone="+998901234561",
            stage=Candidate.Stage.APPLIED,
        )
        Candidate.objects.create(
            vacancy=v,
            first_name="Кандидат2",
            last_name="Тест",
            phone="+998901234562",
            stage=Candidate.Stage.HIRED,
        )
        response = api_client.get("/api/v1/recruitment/candidates/?stage=APPLIED")
        assert response.status_code == 200
        assert response.data["count"] == 1
