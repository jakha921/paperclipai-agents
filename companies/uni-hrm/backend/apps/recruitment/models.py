from __future__ import annotations

from django.conf import settings
from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimestampedModel


class VacancyQuerySet(models.QuerySet):
    def annotate_candidates_count(self) -> VacancyQuerySet:
        return self.annotate(num_candidates=Count("candidates"))


class VacancyManager(models.Manager):
    def get_queryset(self) -> VacancyQuerySet:
        return VacancyQuerySet(self.model, using=self._db)

    def annotate_candidates_count(self) -> VacancyQuerySet:
        return self.get_queryset().annotate_candidates_count()


class Vacancy(TimestampedModel):
    """Вакансия."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Черновик")
        OPEN = "OPEN", _("Открыта")
        CLOSED = "CLOSED", _("Закрыта")

    title = models.JSONField(default=dict, verbose_name=_("Название"))
    position = models.ForeignKey(
        "departments.Position",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="vacancies",
        verbose_name=_("Должность"),
    )
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.PROTECT,
        related_name="vacancies",
        verbose_name=_("Подразделение"),
    )
    requirements = models.TextField(blank=True, verbose_name=_("Требования"))
    responsibilities = models.TextField(blank=True, verbose_name=_("Обязанности"))
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("Статус"),
    )
    vacancies_count = models.IntegerField(default=1, verbose_name=_("Количество мест"))
    deadline = models.DateField(null=True, blank=True, verbose_name=_("Срок подачи"))

    objects = VacancyManager()

    class Meta:
        verbose_name = _("Вакансия")
        verbose_name_plural = _("Вакансии")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        title = self.title
        if isinstance(title, dict):
            return title.get("ru") or title.get("en") or str(title)
        return str(title)

    @property
    def candidates_count(self) -> int:
        return self.candidates.count()


class Candidate(TimestampedModel):
    """Кандидат на вакансию."""

    class Source(models.TextChoices):
        EXTERNAL = "EXTERNAL", _("Внешний")
        INTERNAL = "INTERNAL", _("Внутренний перевод")
        REFERRAL = "REFERRAL", _("Рекомендация")
        HEMIS = "HEMIS", _("HEMIS")

    class Stage(models.TextChoices):
        APPLIED = "APPLIED", _("Подал заявку")
        SCREENING = "SCREENING", _("На проверке")
        INTERVIEW = "INTERVIEW", _("Интервью")
        OFFER = "OFFER", _("Предложение")
        HIRED = "HIRED", _("Принят")
        REJECTED = "REJECTED", _("Отклонён")

    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name="candidates",
        verbose_name=_("Вакансия"),
    )
    first_name = models.CharField(max_length=100, verbose_name=_("Имя"))
    last_name = models.CharField(max_length=100, verbose_name=_("Фамилия"))
    middle_name = models.CharField(max_length=100, blank=True, verbose_name=_("Отчество"))
    phone = models.CharField(max_length=20, verbose_name=_("Телефон"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    resume = models.FileField(upload_to="resumes/%Y/%m/", blank=True, verbose_name=_("Резюме"))
    source = models.CharField(
        max_length=10,
        choices=Source.choices,
        default=Source.EXTERNAL,
        verbose_name=_("Источник"),
    )
    stage = models.CharField(
        max_length=10,
        choices=Stage.choices,
        default=Stage.APPLIED,
        verbose_name=_("Стадия"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Заметки"))
    applied_at = models.DateField(auto_now_add=True, verbose_name=_("Дата заявки"))

    class Meta:
        verbose_name = _("Кандидат")
        verbose_name_plural = _("Кандидаты")
        ordering = ["-applied_at"]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)


class Interview(TimestampedModel):
    """Интервью с кандидатом."""

    class InterviewType(models.TextChoices):
        HR = "HR", _("HR интервью")
        TECHNICAL = "TECHNICAL", _("Техническое")
        FINAL = "FINAL", _("Финальное")

    class Result(models.TextChoices):
        PENDING = "PENDING", _("Ожидание")
        PASS = "PASS", _("Прошёл")
        FAIL = "FAIL", _("Не прошёл")
        HOLD = "HOLD", _("На паузе")

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="interviews",
        verbose_name=_("Кандидат"),
    )
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="interviews",
        verbose_name=_("Интервьюер"),
    )
    scheduled_at = models.DateTimeField(verbose_name=_("Время интервью"))
    interview_type = models.CharField(
        max_length=15,
        choices=InterviewType.choices,
        verbose_name=_("Тип интервью"),
    )
    result = models.CharField(
        max_length=10,
        choices=Result.choices,
        default=Result.PENDING,
        verbose_name=_("Результат"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Заметки"))
    duration_minutes = models.IntegerField(default=60, verbose_name=_("Длительность (мин)"))

    class Meta:
        verbose_name = _("Интервью")
        verbose_name_plural = _("Интервью")
        ordering = ["-scheduled_at"]

    def __str__(self) -> str:
        return f"{self.candidate} — {self.interview_type} ({self.scheduled_at:%d.%m.%Y})"
