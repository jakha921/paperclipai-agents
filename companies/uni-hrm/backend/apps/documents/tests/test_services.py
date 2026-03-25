import datetime
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from apps.departments.models import Department, Employee, Position
from apps.documents.models import DocumentTemplate, GeneratedDocument

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="docuser", email="docuser@test.com", password="pass123"
    )


@pytest.fixture
def department(db):
    return Department.objects.create(
        name={"ru": "Тестовый отдел"},
        code="TEST-DOC",
        department_type="DEPARTMENT",
    )


@pytest.fixture
def position(db):
    return Position.objects.create(
        name={"ru": "Тестовая должность"},
        code="POS-DOC",
        category="PPS",
    )


@pytest.fixture
def employee(db, department, position):
    return Employee.objects.create(
        department=department,
        position=position,
        first_name="Документ",
        last_name="Тестов",
        pinfl="22345678901234",
        passport_series="BB1234567",
        birth_date=datetime.date(1985, 6, 15),
        gender="MALE",
        nationality="uzbek",
        phone="+998901234568",
        hire_date=datetime.date(2022, 1, 1),
    )


@pytest.fixture
def template(db):
    return DocumentTemplate.objects.create(
        name="Приказ о приеме",
        code="hiring_order",
        template_html="<p>Приказ для {{ employee.full_name }}</p>",
        output_format="pdf",
        is_active=True,
    )


@pytest.fixture
def inactive_template(db):
    return DocumentTemplate.objects.create(
        name="Устаревший шаблон",
        code="old_template",
        template_html="<p>Old</p>",
        output_format="pdf",
        is_active=False,
    )


# --- render_template ---


@pytest.mark.django_db
def test_render_template(template):
    from apps.documents.services import render_template

    mock_employee = MagicMock()
    mock_employee.full_name = "Тестов Документ"
    result = render_template(template, {"employee": mock_employee})
    assert "Тестов Документ" in result


@pytest.mark.django_db
def test_render_template_with_extra_data(template):
    from apps.documents.services import render_template

    template.template_html = "<p>{{ employee.full_name }} - {{ date }}</p>"
    template.save()
    mock_employee = MagicMock()
    mock_employee.full_name = "Тестов"
    result = render_template(template, {"employee": mock_employee, "date": "2024-03-15"})
    assert "Тестов" in result
    assert "2024-03-15" in result


# --- generate_document ---


@pytest.mark.django_db
@patch("apps.documents.services.generate_pdf", return_value=b"%PDF-fake-content")
def test_generate_document(mock_pdf, template, employee, user):
    from apps.documents.services import generate_document

    doc = generate_document(
        template_code="hiring_order",
        employee_id=str(employee.id),
        extra_data={},
        user=user,
    )
    assert isinstance(doc, GeneratedDocument)
    assert doc.template == template
    assert doc.employee == employee
    assert doc.generated_by == user
    assert doc.file
    mock_pdf.assert_called_once()


@pytest.mark.django_db
def test_generate_document_template_not_found(employee, user):
    from apps.documents.services import generate_document

    with pytest.raises(DocumentTemplate.DoesNotExist):
        generate_document(
            template_code="nonexistent",
            employee_id=str(employee.id),
            extra_data={},
            user=user,
        )


@pytest.mark.django_db
@patch("apps.documents.services.generate_pdf", return_value=b"%PDF-fake")
def test_generate_document_inactive_template(mock_pdf, inactive_template, employee, user):
    from apps.documents.services import generate_document

    with pytest.raises(DocumentTemplate.DoesNotExist):
        generate_document(
            template_code="old_template",
            employee_id=str(employee.id),
            extra_data={},
            user=user,
        )


# --- generate_employee_excel ---


@pytest.mark.django_db
def test_generate_employee_excel(employee):
    from apps.documents.services import generate_employee_excel

    result = generate_employee_excel({})
    assert isinstance(result, bytes)
    assert len(result) > 0


@pytest.mark.django_db
def test_generate_employee_excel_with_department_filter(employee, department):
    from apps.documents.services import generate_employee_excel

    result = generate_employee_excel({"department_id": str(department.id)})
    assert isinstance(result, bytes)


@pytest.mark.django_db
def test_generate_employee_excel_with_status_filter(employee):
    from apps.documents.services import generate_employee_excel

    result = generate_employee_excel({"status": "ACTIVE"})
    assert isinstance(result, bytes)
