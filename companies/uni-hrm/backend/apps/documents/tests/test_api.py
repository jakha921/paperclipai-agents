import datetime

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.departments.models import Department, Employee, Position
from apps.documents.models import DocumentTemplate, GeneratedDocument


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, django_user_model):
    user = django_user_model.objects.create_user(
        username="testuser",
        email="testuser@test.com",
        password="pass123",
    )
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def department(db):
    return Department.objects.create(
        name={"ru": "Отдел документов"},
        code="DOC-DEPT",
        department_type="DEPARTMENT",
    )


@pytest.fixture
def position(db):
    return Position.objects.create(
        name={"ru": "Инженер"},
        code="DOC-POS",
        category="AUP",
    )


@pytest.fixture
def employee(db, department, position):
    return Employee.objects.create(
        department=department,
        position=position,
        first_name="Документ",
        last_name="Тестов",
        pinfl="32345678901234",
        passport_series="CC1234567",
        birth_date=datetime.date(1990, 1, 1),
        gender="MALE",
        nationality="uzbek",
        phone="+998901234569",
        hire_date=datetime.date(2023, 1, 1),
    )


@pytest.fixture
def template(db):
    return DocumentTemplate.objects.create(
        name="Test Template",
        code="test",
        template_html="<p>test {{ employee.full_name }}</p>",
        output_format="pdf",
    )


# --- Templates ---


@pytest.mark.django_db
def test_templates_list(auth_client, template):
    response = auth_client.get("/api/v1/documents/templates/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_template_create(auth_client):
    data = {
        "name": "Новый шаблон",
        "code": "new_tpl",
        "template_html": "<p>Hello</p>",
        "output_format": "pdf",
    }
    response = auth_client.post("/api/v1/documents/templates/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["code"] == "new_tpl"


@pytest.mark.django_db
def test_template_detail(auth_client, template):
    response = auth_client.get(f"/api/v1/documents/templates/{template.id}/")
    assert response.status_code == 200
    assert response.data["code"] == "test"


@pytest.mark.django_db
def test_template_update(auth_client, template):
    data = {
        "name": "Updated Template",
        "code": "test",
        "template_html": "<p>updated</p>",
        "output_format": "pdf",
    }
    response = auth_client.put(f"/api/v1/documents/templates/{template.id}/", data, format="json")
    assert response.status_code == 200
    assert response.data["name"] == "Updated Template"


@pytest.mark.django_db
def test_templates_no_auth(api_client):
    response = api_client.get("/api/v1/documents/templates/")
    assert response.status_code in (401, 403)


# --- Generated Documents ---


@pytest.mark.django_db
def test_documents_list(auth_client):
    response = auth_client.get("/api/v1/documents/documents/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_document_download_no_file(auth_client, template, employee, django_user_model):
    user = django_user_model.objects.get(username="testuser")
    doc = GeneratedDocument.objects.create(
        template=template,
        employee=employee,
        generated_by=user,
        data={},
    )
    response = auth_client.get(f"/api/v1/documents/documents/{doc.id}/download/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


# --- Analytics ---


@pytest.mark.django_db
def test_analytics_dashboard(auth_client):
    response = auth_client.get("/api/v1/documents/analytics/dashboard/")
    assert response.status_code == 200
    data = response.json()
    assert "total_employees" in data


@pytest.mark.django_db
def test_analytics_turnover(auth_client):
    response = auth_client.get("/api/v1/documents/analytics/turnover/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.django_db
def test_analytics_turnover_with_months(auth_client):
    response = auth_client.get("/api/v1/documents/analytics/turnover/?months=6")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 6


@pytest.mark.django_db
def test_analytics_departments(auth_client):
    response = auth_client.get("/api/v1/documents/analytics/departments/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.django_db
def test_analytics_demographics(auth_client):
    response = auth_client.get("/api/v1/documents/analytics/demographics/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "gender_distribution" in data


# --- Reports ---


@pytest.mark.django_db
def test_reports_payroll_excel_missing_params(auth_client):
    response = auth_client.post("/api/v1/documents/reports/payroll_excel/", {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_reports_payroll_excel(auth_client):
    response = auth_client.post(
        "/api/v1/documents/reports/payroll_excel/",
        {"year": 2024, "month": 3},
        format="json",
    )
    assert response.status_code == 200
    assert (
        response["Content-Type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@pytest.mark.django_db
def test_reports_employees_excel(auth_client):
    response = auth_client.post("/api/v1/documents/reports/employees_excel/", {}, format="json")
    assert response.status_code == 200
    assert (
        response["Content-Type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@pytest.mark.django_db
def test_reports_employees_excel_with_filter(auth_client, department):
    response = auth_client.post(
        "/api/v1/documents/reports/employees_excel/",
        {"department_id": str(department.id), "status": "ACTIVE"},
        format="json",
    )
    assert response.status_code == 200
