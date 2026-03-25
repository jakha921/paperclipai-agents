export const EMPLOYEE_STATUS_LABELS: Record<string, string> = {
  ACTIVE: 'Работает',
  ON_LEAVE: 'В отпуске',
  DISMISSED: 'Уволен',
};

export const EMPLOYEE_STATUS_COLORS: Record<string, string> = {
  ACTIVE: 'bg-emerald-100 text-emerald-700',
  ON_LEAVE: 'bg-amber-100 text-amber-700',
  DISMISSED: 'bg-red-100 text-red-700',
};

export const LEAVE_STATUS_LABELS: Record<string, string> = {
  PENDING: 'На рассмотрении',
  APPROVED: 'Одобрен',
  REJECTED: 'Отклонён',
  CANCELLED: 'Отменён',
};

export const LEAVE_STATUS_COLORS: Record<string, string> = {
  PENDING: 'bg-amber-100 text-amber-700',
  APPROVED: 'bg-emerald-100 text-emerald-700',
  REJECTED: 'bg-red-100 text-red-700',
  CANCELLED: 'bg-slate-100 text-slate-600',
};

export const PAYROLL_STATUS_LABELS: Record<string, string> = {
  DRAFT: 'Черновик',
  CALCULATED: 'Рассчитан',
  APPROVED: 'Утверждён',
  PAID: 'Выплачен',
};

export const PAYROLL_STATUS_COLORS: Record<string, string> = {
  DRAFT: 'bg-slate-100 text-slate-600',
  CALCULATED: 'bg-blue-100 text-blue-700',
  APPROVED: 'bg-emerald-100 text-emerald-700',
  PAID: 'bg-indigo-100 text-indigo-700',
};

export const ATTENDANCE_STATUS_LABELS: Record<string, string> = {
  PRESENT: 'Присутствует',
  ABSENT: 'Отсутствует',
  LATE: 'Опоздание',
  ON_LEAVE: 'Отпуск',
  SICK: 'Больничный',
  HOLIDAY: 'Праздник',
};

export const ATTENDANCE_STATUS_COLORS: Record<string, string> = {
  PRESENT: 'bg-emerald-100 text-emerald-700',
  ABSENT: 'bg-red-100 text-red-700',
  LATE: 'bg-amber-100 text-amber-700',
  ON_LEAVE: 'bg-blue-100 text-blue-700',
  SICK: 'bg-orange-100 text-orange-700',
  HOLIDAY: 'bg-slate-100 text-slate-600',
};

export const EMPLOYMENT_HISTORY_LABELS: Record<string, string> = {
  HIRED: 'Принят',
  TRANSFERRED: 'Переведён',
  PROMOTED: 'Повышен',
  DISMISSED: 'Уволен',
};

export const VACANCY_STATUS_LABELS: Record<string, string> = {
  DRAFT: 'Черновик',
  OPEN: 'Открыта',
  CLOSED: 'Закрыта',
};

export const VACANCY_STATUS_COLORS: Record<string, string> = {
  DRAFT: 'bg-slate-100 text-slate-700',
  OPEN: 'bg-emerald-100 text-emerald-700',
  CLOSED: 'bg-red-100 text-red-700',
};

export const CANDIDATE_STAGE_LABELS: Record<string, string> = {
  APPLIED: 'Заявка',
  SCREENING: 'Проверка',
  INTERVIEW: 'Интервью',
  OFFER: 'Предложение',
  HIRED: 'Принят',
  REJECTED: 'Отклонён',
};

export const CANDIDATE_STAGE_COLORS: Record<string, string> = {
  APPLIED: 'bg-blue-100 text-blue-700',
  SCREENING: 'bg-yellow-100 text-yellow-700',
  INTERVIEW: 'bg-purple-100 text-purple-700',
  OFFER: 'bg-orange-100 text-orange-700',
  HIRED: 'bg-emerald-100 text-emerald-700',
  REJECTED: 'bg-red-100 text-red-700',
};

export const CANDIDATE_SOURCE_LABELS: Record<string, string> = {
  EXTERNAL: 'Внешний',
  INTERNAL: 'Внутренний',
  REFERRAL: 'Рекомендация',
  HEMIS: 'HEMIS',
};

export const INTERVIEW_TYPE_LABELS: Record<string, string> = {
  HR: 'HR интервью',
  TECHNICAL: 'Техническое',
  FINAL: 'Финальное',
};

export const INTERVIEW_RESULT_LABELS: Record<string, string> = {
  PENDING: 'Ожидание',
  PASS: 'Прошёл',
  FAIL: 'Не прошёл',
  HOLD: 'На паузе',
};

export const CONTEST_STATUS_LABELS: Record<string, string> = {
  OPEN: 'Открыт',
  REVIEWING: 'На рассмотрении',
  CLOSED: 'Закрыт',
};

export const CONTEST_STATUS_COLORS: Record<string, string> = {
  OPEN: 'bg-green-100 text-green-800',
  REVIEWING: 'bg-yellow-100 text-yellow-800',
  CLOSED: 'bg-gray-100 text-gray-800',
};

export const LOAD_TYPE_LABELS: Record<string, string> = {
  PRIMARY: 'Основная',
  ADDITIONAL: 'Дополнительная',
};

export const APPRAISAL_CYCLE_STATUS_LABELS: Record<string, string> = {
  planning: 'Планирование',
  active: 'Активный',
  review: 'На рассмотрении',
  completed: 'Завершён',
};

export const APPRAISAL_CYCLE_STATUS_COLORS: Record<string, string> = {
  planning: 'bg-slate-100 text-slate-700',
  active: 'bg-green-100 text-green-700',
  review: 'bg-amber-100 text-amber-700',
  completed: 'bg-indigo-100 text-indigo-700',
};

export const EMPLOYEE_APPRAISAL_STATUS_LABELS: Record<string, string> = {
  pending: 'Ожидает',
  self_review: 'Самооценка',
  manager_review: 'Оценка руководителя',
  completed: 'Завершена',
};

export const EMPLOYEE_APPRAISAL_STATUS_COLORS: Record<string, string> = {
  pending: 'bg-slate-100 text-slate-600',
  self_review: 'bg-blue-100 text-blue-700',
  manager_review: 'bg-amber-100 text-amber-700',
  completed: 'bg-green-100 text-green-700',
};

export const TRAINING_STATUS_LABELS: Record<string, string> = {
  enrolled: 'Записан',
  in_progress: 'В процессе',
  completed: 'Завершён',
  cancelled: 'Отменён',
};

export const TRAINING_STATUS_COLORS: Record<string, string> = {
  enrolled: 'bg-blue-100 text-blue-700',
  in_progress: 'bg-amber-100 text-amber-700',
  completed: 'bg-green-100 text-green-700',
  cancelled: 'bg-slate-100 text-slate-500',
};

export const TRAINING_TYPE_LABELS: Record<string, string> = {
  internal: 'Внутреннее',
  external: 'Внешнее',
  online: 'Онлайн',
};

export const KPI_CATEGORY_LABELS: Record<string, string> = {
  academic: 'Академическая',
  administrative: 'Административная',
  research: 'Научная',
  service: 'Служебная',
};
