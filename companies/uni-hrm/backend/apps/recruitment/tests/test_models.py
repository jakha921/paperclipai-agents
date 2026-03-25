import pytest

from apps.recruitment.models import Candidate, Vacancy


@pytest.mark.django_db
class TestVacancyModel:
    def test_create_vacancy(self, department):
        v = Vacancy.objects.create(
            title={"ru": "Тест вакансия"},
            department=department,
            status=Vacancy.Status.DRAFT,
        )
        assert v.pk is not None
        assert str(v) == "Тест вакансия"

    def test_candidates_count_zero(self, department):
        v = Vacancy.objects.create(title={"ru": "Вакансия"}, department=department)
        assert v.candidates_count == 0

    def test_status_choices(self):
        assert Vacancy.Status.DRAFT == "DRAFT"
        assert Vacancy.Status.OPEN == "OPEN"
        assert Vacancy.Status.CLOSED == "CLOSED"

    def test_str_fallback_to_en(self, department):
        v = Vacancy.objects.create(
            title={"en": "English Title"},
            department=department,
        )
        assert str(v) == "English Title"


@pytest.mark.django_db
class TestCandidateModel:
    def test_full_name_without_middle(self, department):
        v = Vacancy.objects.create(title={"ru": "Вакансия"}, department=department)
        c = Candidate.objects.create(
            vacancy=v,
            first_name="Иван",
            last_name="Иванов",
            phone="+998901234567",
        )
        assert c.full_name == "Иванов Иван"

    def test_full_name_with_middle(self, department):
        v = Vacancy.objects.create(title={"ru": "Вакансия"}, department=department)
        c = Candidate.objects.create(
            vacancy=v,
            first_name="Иван",
            last_name="Иванов",
            middle_name="Петрович",
            phone="+998901234567",
        )
        assert c.full_name == "Иванов Иван Петрович"

    def test_stage_defaults_to_applied(self, department):
        v = Vacancy.objects.create(title={"ru": "Вакансия"}, department=department)
        c = Candidate.objects.create(
            vacancy=v,
            first_name="Тест",
            last_name="Тестов",
            phone="+998901234567",
        )
        assert c.stage == Candidate.Stage.APPLIED

    def test_stage_choices(self):
        assert Candidate.Stage.APPLIED == "APPLIED"
        assert Candidate.Stage.HIRED == "HIRED"
        assert Candidate.Stage.REJECTED == "REJECTED"
