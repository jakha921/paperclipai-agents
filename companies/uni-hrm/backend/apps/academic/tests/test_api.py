import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.academic.models import (
    AcademicDegree,
    AcademicLoad,
    AcademicTitle,
    PositionContest,
    Subject,
)


@pytest.mark.django_db
class TestAcademicDegreeAPI:
    def test_list_degrees(self, auth_client):
        AcademicDegree.objects.create(code="phd", name={"ru": "PhD"})
        response = auth_client.get(reverse("academic-degrees-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_create_degree(self, auth_client):
        response = auth_client.post(
            reverse("academic-degrees-list"),
            {"code": "dsc", "name": {"ru": "DSc"}},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["code"] == "dsc"

    def test_unauthenticated(self):
        client = APIClient()
        response = client.get(reverse("academic-degrees-list"))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAcademicTitleAPI:
    def test_list_titles(self, auth_client):
        AcademicTitle.objects.create(code="professor", name={"ru": "Профессор"})
        response = auth_client.get(reverse("academic-titles-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_create_title(self, auth_client):
        response = auth_client.post(
            reverse("academic-titles-list"),
            {"code": "docent", "name": {"ru": "Доцент"}},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestSubjectAPI:
    def test_list_subjects(self, auth_client, department):
        Subject.objects.create(code="MATH101", name={"ru": "Математика"}, department=department)
        response = auth_client.get(reverse("subjects-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_filter_by_department(self, auth_client, department):
        Subject.objects.create(code="MATH101", name={"ru": "Математика"}, department=department)
        response = auth_client.get(reverse("subjects-list"), {"department": str(department.id)})
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestAcademicLoadAPI:
    def test_list_loads(self, auth_client):
        response = auth_client.get(reverse("academic-loads-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_summary(self, auth_client, employee, department):
        subject = Subject.objects.create(
            code="CS101", name={"ru": "Информатика"}, department=department
        )
        AcademicLoad.objects.create(
            employee=employee,
            subject=subject,
            academic_year="2024-2025",
            semester=1,
            lecture_hours=30,
            seminar_hours=20,
            lab_hours=10,
        )
        response = auth_client.get(
            reverse("academic-loads-summary"),
            {
                "employee": str(employee.id),
                "academic_year": "2024-2025",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_hours"] == 60
        assert response.data["exceeds_limit"] is False

    def test_summary_missing_params(self, auth_client):
        response = auth_client.get(reverse("academic-loads-summary"))
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPositionContestAPI:
    def test_list_contests(self, auth_client):
        response = auth_client.get(reverse("position-contests-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_close_contest(self, auth_client, department, position):
        contest = PositionContest.objects.create(
            department=department,
            position=position,
            application_deadline="2025-06-01",
        )
        response = auth_client.post(reverse("position-contests-close", kwargs={"pk": contest.pk}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "CLOSED"

    def test_close_non_open_contest(self, auth_client, department, position):
        contest = PositionContest.objects.create(
            department=department,
            position=position,
            application_deadline="2025-06-01",
            status=PositionContest.Status.CLOSED,
        )
        response = auth_client.post(reverse("position-contests-close", kwargs={"pk": contest.pk}))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_set_winner(self, auth_client, department, position, employee):
        contest = PositionContest.objects.create(
            department=department,
            position=position,
            application_deadline="2025-06-01",
        )
        response = auth_client.post(
            reverse("position-contests-set-winner", kwargs={"pk": contest.pk}),
            {"winner_id": str(employee.pk)},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "CLOSED"
