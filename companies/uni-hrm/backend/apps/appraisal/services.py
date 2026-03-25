from __future__ import annotations

from decimal import Decimal

from apps.appraisal.models import EmployeeAppraisal


def calculate_weighted_score(appraisal: EmployeeAppraisal) -> Decimal:
    """Вычислить взвешенный итоговый балл аттестации.

    Для каждого AppraisalScore:
    - Если final_score установлен, используем его
    - Иначе среднее self_score и manager_score
    Взвешенная сумма нормализуется к шкале 10.
    """
    scores = appraisal.scores.select_related("kpi").all()
    if not scores:
        return Decimal("0.00")

    total_weighted = Decimal("0.00")
    total_weight = Decimal("0.00")

    for score in scores:
        # Определяем значение оценки
        if score.final_score is not None:
            value = score.final_score
        elif score.self_score is not None and score.manager_score is not None:
            value = Decimal(score.self_score + score.manager_score) / Decimal("2")
        elif score.self_score is not None:
            value = Decimal(score.self_score)
        elif score.manager_score is not None:
            value = Decimal(score.manager_score)
        else:
            continue

        kpi = score.kpi
        # Нормализуем оценку к шкале 10 и умножаем на вес
        normalized = value / Decimal(kpi.max_score) * Decimal("10")
        total_weighted += normalized * kpi.weight
        total_weight += kpi.weight

    if total_weight == 0:
        return Decimal("0.00")

    result = total_weighted / total_weight
    return result.quantize(Decimal("0.01"))


def get_rating_label(score: Decimal) -> str:
    """Получить текстовую оценку по баллу."""
    if score >= Decimal("8.5"):
        return "Отлично"
    if score >= Decimal("7.0"):
        return "Хорошо"
    if score >= Decimal("5.0"):
        return "Удовлетворительно"
    return "Неудовлетворительно"
