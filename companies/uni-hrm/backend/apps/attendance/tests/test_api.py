import datetime
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from apps.attendance.models import AttendanceRecord, TimeSheet, WorkSchedule
from apps.departments.models import Department, Employee, Position

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin_att", email="admin_att@test.com", password="testpass123"
    )


@pytest.fixture
def department(db):
    return Department.objects.create(
        name={"ru": "Тестовый отдел"},
        code="TEST-ATT",
        department_type="DEPARTMENT",
    )


@pytest.fixture
def position(db):
    return Position.objects.create(
        name={"ru": "Тестовая должность"},
        code="POS-ATT",
        category="PPS",
    )


@pytest.fixture
def employee(db, department, position):
    return Employee.objects.create(
        department=department,
        position=position,
        first_name="Тест",
        last_name="Тестов",
        pinfl="12345678901234",
        passport_series="AA1234567",
        birth_date=datetime.date(1990, 1, 1),
        gender="MALE",
        nationality="uzbek",
        phone="+998901234567",
        hire_date=datetime.date(2023, 1, 1),
    )


@pytest.fixture
def work_schedule(db):
    return WorkSchedule.objects.create(
        name="Стандартный",
        schedule_type="5/2",
        work_start=datetime.time(9, 0),
        work_end=datetime.time(18, 0),
        working_days=[1, 2, 3, 4, 5],
    )


@pytest.fixture
def attendance_record(db, employee):
    return AttendanceRecord.objects.create(
        employee=employee,
        date=datetime.date(2024, 3, 15),
        check_in=datetime.time(9, 0),
        check_out=datetime.time(18, 0),
        status=AttendanceRecord.Status.PRESENT,
        worked_hours=Decimal("8.00"),
        source=AttendanceRecord.Source.MANUAL,
    )


@pytest.fixture
def timesheet(db, employee):
    return TimeSheet.objects.create(
        employee=employee,
        month=3,
        year=2024,
        total_working_days=22,
        days_present=20,
        days_absent=1,
        days_late=1,
        total_hours=Decimal("160.00"),
        status=TimeSheet.Status.DRAFT,
    )


# --- Work Schedule tests ---


@pytest.mark.django_db
def test_work_schedules_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/attendance/schedules/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_work_schedule_create(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    data = {
        "name": "Новый график",
        "schedule_type": "5/2",
        "work_start": "09:00",
        "work_end": "18:00",
        "working_days": [1, 2, 3, 4, 5],
    }
    response = api_client.post("/api/v1/attendance/schedules/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "Новый график"


@pytest.mark.django_db
def test_work_schedule_detail(api_client, admin_user, work_schedule):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get(f"/api/v1/attendance/schedules/{work_schedule.id}/")
    assert response.status_code == 200
    assert response.data["name"] == "Стандартный"


# --- Attendance Record tests ---


@pytest.mark.django_db
def test_attendance_records_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/attendance/records/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_attendance_record_create(api_client, admin_user, employee):
    api_client.force_authenticate(user=admin_user)
    data = {
        "employee": str(employee.id),
        "date": "2024-03-20",
        "check_in": "09:00",
        "check_out": "18:00",
        "status": "PRESENT",
        "source": "MANUAL",
    }
    response = api_client.post("/api/v1/attendance/records/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == "PRESENT"


@pytest.mark.django_db
def test_attendance_record_duplicate_date(api_client, admin_user, employee, attendance_record):
    """Unique constraint: same employee + same date should fail."""
    api_client.force_authenticate(user=admin_user)
    data = {
        "employee": str(employee.id),
        "date": "2024-03-15",  # same date as fixture
        "check_in": "10:00",
        "check_out": "19:00",
        "status": "LATE",
        "source": "MANUAL",
    }
    response = api_client.post("/api/v1/attendance/records/", data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_attendance_record_check_out_before_check_in(api_client, admin_user, employee):
    """Validation: check_out must be after check_in."""
    api_client.force_authenticate(user=admin_user)
    data = {
        "employee": str(employee.id),
        "date": "2024-03-21",
        "check_in": "18:00",
        "check_out": "09:00",  # before check_in
        "status": "PRESENT",
        "source": "MANUAL",
    }
    response = api_client.post("/api/v1/attendance/records/", data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_attendance_records_filter_by_status(api_client, admin_user, attendance_record):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/attendance/records/?status=PRESENT")
    assert response.status_code == 200
    results = response.data.get("results", response.data)
    assert len(results) >= 1


@pytest.mark.django_db
def test_attendance_records_filter_by_date_range(api_client, admin_user, attendance_record):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/attendance/records/?date_from=2024-03-01&date_to=2024-03-31")
    assert response.status_code == 200
    results = response.data.get("results", response.data)
    assert len(results) >= 1


@pytest.mark.django_db
def test_attendance_records_filter_by_department(
    api_client, admin_user, attendance_record, department
):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get(f"/api/v1/attendance/records/?department={department.id}")
    assert response.status_code == 200


@pytest.mark.django_db
def test_attendance_record_update(api_client, admin_user, attendance_record):
    api_client.force_authenticate(user=admin_user)
    data = {
        "employee": str(attendance_record.employee.id),
        "date": str(attendance_record.date),
        "status": "LATE",
        "check_in": "09:30",
        "check_out": "18:00",
        "source": "MANUAL",
    }
    response = api_client.put(
        f"/api/v1/attendance/records/{attendance_record.id}/", data, format="json"
    )
    assert response.status_code == 200
    assert response.data["status"] == "LATE"


@pytest.mark.django_db
def test_attendance_record_no_auth(api_client):
    """Unauthenticated requests should be rejected."""
    response = api_client.get("/api/v1/attendance/records/")
    assert response.status_code in (401, 403)


# --- Timesheet tests ---


@pytest.mark.django_db
def test_timesheets_list(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/attendance/timesheets/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_timesheet_create(api_client, admin_user, employee):
    api_client.force_authenticate(user=admin_user)
    data = {
        "employee": str(employee.id),
        "month": 4,
        "year": 2024,
        "total_working_days": 22,
        "days_present": 22,
        "days_absent": 0,
        "days_late": 0,
        "days_on_leave": 0,
        "total_hours": "176.00",
        "overtime_hours": "0.00",
        "status": "DRAFT",
    }
    response = api_client.post("/api/v1/attendance/timesheets/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["month"] == 4


@pytest.mark.django_db
def test_timesheet_submit(api_client, admin_user, timesheet):
    """DRAFT -> SUBMITTED transition."""
    api_client.force_authenticate(user=admin_user)
    response = api_client.post(f"/api/v1/attendance/timesheets/{timesheet.id}/submit/")
    assert response.status_code == 200
    assert response.data["status"] == "SUBMITTED"


@pytest.mark.django_db
def test_timesheet_approve(api_client, admin_user, timesheet):
    """SUBMITTED -> APPROVED transition."""
    api_client.force_authenticate(user=admin_user)
    # First submit
    timesheet.status = TimeSheet.Status.SUBMITTED
    timesheet.save(update_fields=["status"])
    # Then approve
    response = api_client.post(f"/api/v1/attendance/timesheets/{timesheet.id}/approve/")
    assert response.status_code == 200
    assert response.data["status"] == "APPROVED"


@pytest.mark.django_db
def test_timesheet_submit_non_draft_fails(api_client, admin_user, timesheet):
    """Only DRAFT can be submitted."""
    api_client.force_authenticate(user=admin_user)
    timesheet.status = TimeSheet.Status.SUBMITTED
    timesheet.save(update_fields=["status"])
    response = api_client.post(f"/api/v1/attendance/timesheets/{timesheet.id}/submit/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_timesheet_approve_non_submitted_fails(api_client, admin_user, timesheet):
    """Only SUBMITTED can be approved."""
    api_client.force_authenticate(user=admin_user)
    # timesheet is DRAFT by default
    response = api_client.post(f"/api/v1/attendance/timesheets/{timesheet.id}/approve/")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_timesheet_filter_by_year_month(api_client, admin_user, timesheet):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/attendance/timesheets/?year=2024&month=3")
    assert response.status_code == 200
    results = response.data.get("results", response.data)
    assert len(results) >= 1


@pytest.mark.django_db
def test_timesheet_filter_by_status(api_client, admin_user, timesheet):
    api_client.force_authenticate(user=admin_user)
    response = api_client.get("/api/v1/attendance/timesheets/?status=DRAFT")
    assert response.status_code == 200
    results = response.data.get("results", response.data)
    assert len(results) >= 1


# --- Bulk create ---


@pytest.mark.django_db
def test_bulk_create_attendance(api_client, admin_user, employee):
    api_client.force_authenticate(user=admin_user)
    data = {
        "records": [
            {
                "employee": str(employee.id),
                "date": "2024-04-01",
                "check_in": "09:00",
                "check_out": "18:00",
                "status": "PRESENT",
                "source": "MANUAL",
            },
            {
                "employee": str(employee.id),
                "date": "2024-04-02",
                "check_in": "09:15",
                "check_out": "18:00",
                "status": "LATE",
                "source": "MANUAL",
            },
        ]
    }
    response = api_client.post("/api/v1/attendance/records/bulk_create/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.data) == 2
