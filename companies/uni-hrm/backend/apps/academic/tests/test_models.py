import pytest
from django.db import IntegrityError

from apps.academic.models import (
    AcademicDegree,
    AcademicLoad,
    AcademicTitle,
    EmployeeAcademic,
    PositionContest,
    Subject,
)


@pytest.mark.django_db
class TestAcademicDegree:
    def test_create_degree(self):
        degree = AcademicDegree.objects.create(
            code="phd",
            name={"ru": "PhD", "uz": "PhD", "en": "PhD"},
        )
        assert str(degree) == "PhD"
        assert degree.code == "phd"

    def test_unique_code(self):
        AcademicDegree.objects.create(code="phd", name={"ru": "PhD"})
        with pytest.raises(IntegrityError):
            AcademicDegree.objects.create(code="phd", name={"ru": "PhD 2"})


@pytest.mark.django_db
class TestAcademicTitle:
    def test_create_title(self):
        title = AcademicTitle.objects.create(
            code="professor",
            name={"ru": "Профессор", "en": "Professor"},
        )
        assert str(title) == "Профессор"

    def test_unique_code(self):
        AcademicTitle.objects.create(code="professor", name={"ru": "Профессор"})
        with pytest.raises(IntegrityError):
            AcademicTitle.objects.create(code="professor", name={"ru": "Ещё"})


@pytest.mark.django_db
class TestSubject:
    def test_create_subject(self, department):
        subject = Subject.objects.create(
            code="MATH101",
            name={"ru": "Математика", "en": "Mathematics"},
            department=department,
            credits=4,
        )
        assert str(subject) == "Математика"
        assert subject.is_active is True

    def test_unique_code(self, department):
        Subject.objects.create(code="MATH101", name={"ru": "Математика"}, department=department)
        with pytest.raises(IntegrityError):
            Subject.objects.create(code="MATH101", name={"ru": "Другая"}, department=department)


@pytest.mark.django_db
class TestAcademicLoad:
    def test_total_hours(self, employee, department):
        subject = Subject.objects.create(
            code="CS101",
            name={"ru": "Информатика"},
            department=department,
        )
        load = AcademicLoad.objects.create(
            employee=employee,
            subject=subject,
            academic_year="2024-2025",
            semester=1,
            lecture_hours=30,
            seminar_hours=20,
            lab_hours=10,
        )
        assert load.total_hours == 60

    def test_unique_together(self, employee, department):
        subject = Subject.objects.create(
            code="CS102",
            name={"ru": "Программирование"},
            department=department,
        )
        AcademicLoad.objects.create(
            employee=employee,
            subject=subject,
            academic_year="2024-2025",
            semester=1,
        )
        with pytest.raises(IntegrityError):
            AcademicLoad.objects.create(
                employee=employee,
                subject=subject,
                academic_year="2024-2025",
                semester=1,
            )


@pytest.mark.django_db
class TestEmployeeAcademic:
    def test_create(self, employee):
        degree = AcademicDegree.objects.create(code="phd", name={"ru": "PhD"})
        title = AcademicTitle.objects.create(code="docent", name={"ru": "Доцент"})
        academic = EmployeeAcademic.objects.create(
            employee=employee,
            degree=degree,
            title=title,
            specialization="Computer Science",
        )
        assert "PhD" in str(academic)
        assert "Доцент" in str(academic)


@pytest.mark.django_db
class TestPositionContest:
    def test_create(self, department, position):
        contest = PositionContest.objects.create(
            department=department,
            position=position,
            application_deadline="2025-06-01",
        )
        assert contest.status == PositionContest.Status.OPEN
        assert contest.winner is None
