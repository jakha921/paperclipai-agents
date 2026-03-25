import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin_appraisal", email="admin_appr@test.com", password="testpass123"
    )


@pytest.mark.django_db
def test_appraisal_cycles_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/appraisals/cycles/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_kpi_indicators_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/appraisals/kpis/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_employee_appraisals_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/appraisals/employee-appraisals/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_appraisal_scores_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/appraisals/scores/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_training_programs_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/appraisals/training-programs/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_training_records_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/appraisals/training-records/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_appraisal_cycle(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    data = {
        "name": "2025 H1",
        "start_date": "2025-01-01",
        "end_date": "2025-06-30",
        "status": "planning",
    }
    response = api_client.post("/api/v1/appraisals/cycles/", data, format="json")
    assert response.status_code == 201
    assert response.data["name"] == "2025 H1"


@pytest.mark.django_db
def test_create_kpi_indicator(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    data = {
        "name": {"ru": "Публикации", "en": "Publications"},
        "category": "academic",
        "weight": "30.00",
        "max_score": 10,
    }
    response = api_client.post("/api/v1/appraisals/kpis/", data, format="json")
    assert response.status_code == 201


@pytest.mark.django_db
def test_create_training_program(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    data = {
        "name": {"ru": "Python курс"},
        "training_type": "online",
        "duration_hours": 40,
        "cost": "0.00",
    }
    response = api_client.post("/api/v1/appraisals/training-programs/", data, format="json")
    assert response.status_code == 201
