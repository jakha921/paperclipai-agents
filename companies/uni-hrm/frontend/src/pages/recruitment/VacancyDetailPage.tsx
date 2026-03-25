import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, UserCheck, UserX } from 'lucide-react';
import {
  useVacancy,
  useCreateCandidate,
  useHireCandidate,
  useRejectCandidate,
} from '@/features/recruitment';
import type { CandidateListItem, CandidateSource, CreateCandidateData } from '@/features/recruitment';
import {
  VACANCY_STATUS_COLORS,
  VACANCY_STATUS_LABELS,
  CANDIDATE_STAGE_COLORS,
  CANDIDATE_STAGE_LABELS,
} from '@/shared/constants/statuses';

function getVacancyTitle(title: { ru?: string; uz?: string; en?: string } | string): string {
  if (typeof title === 'object') return title.ru ?? title.en ?? '';
  return String(title);
}

export default function VacancyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [showAddCandidate, setShowAddCandidate] = useState(false);

  const { data: vacancy, isLoading } = useVacancy(id ?? '');
  const createCandidate = useCreateCandidate();
  const hireCandidate = useHireCandidate();
  const rejectCandidate = useRejectCandidate();

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <div className="animate-pulse h-8 bg-slate-200 rounded w-1/3" />
        <div className="animate-pulse h-32 bg-slate-200 rounded" />
      </div>
    );
  }

  if (!vacancy) return null;

  const titleText = getVacancyTitle(vacancy.title);
  const candidates = vacancy.candidates ?? [];

  const handleAddCandidate = async (formData: Omit<CreateCandidateData, 'vacancy'>) => {
    await createCandidate.mutateAsync({ ...formData, vacancy: id ?? '' });
    setShowAddCandidate(false);
  };

  const handleHire = async (candidateId: string) => {
    const result = await hireCandidate.mutateAsync(candidateId);
    alert(`Сотрудник создан. ID: ${result.employee_id}`);
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <button
          onClick={() => navigate('/recruitment/vacancies')}
          className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700 mb-4 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Назад
        </button>
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold font-heading text-slate-900">{titleText}</h1>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-sm text-slate-500">{vacancy.department_name}</span>
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${VACANCY_STATUS_COLORS[vacancy.status] ?? ''}`}
              >
                {VACANCY_STATUS_LABELS[vacancy.status] ?? vacancy.status}
              </span>
              <span className="text-sm text-slate-500">{vacancy.vacancies_count} мест</span>
            </div>
          </div>
          <button
            onClick={() => setShowAddCandidate(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Добавить кандидата
          </button>
        </div>
      </div>

      {(vacancy.requirements || vacancy.responsibilities) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {vacancy.requirements && (
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <h3 className="text-sm font-semibold text-slate-900 mb-2">Требования</h3>
              <p className="text-sm text-slate-600 whitespace-pre-line">{vacancy.requirements}</p>
            </div>
          )}
          {vacancy.responsibilities && (
            <div className="bg-white rounded-xl border border-slate-200 p-4">
              <h3 className="text-sm font-semibold text-slate-900 mb-2">Обязанности</h3>
              <p className="text-sm text-slate-600 whitespace-pre-line">
                {vacancy.responsibilities}
              </p>
            </div>
          )}
        </div>
      )}

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-200">
          <h2 className="text-base font-semibold text-slate-900">
            Кандидаты ({candidates.length})
          </h2>
        </div>
        {candidates.length === 0 ? (
          <div className="py-10 text-center text-sm text-slate-400">Кандидатов пока нет</div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200">
                <th className="text-left px-4 py-3 font-medium text-slate-600">Кандидат</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Телефон</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Стадия</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Источник</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Дата</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">Действия</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => (
                <CandidateRow
                  key={c.id}
                  candidate={c}
                  onHire={() => handleHire(c.id)}
                  onReject={() => rejectCandidate.mutate(c.id)}
                />
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showAddCandidate && (
        <AddCandidateModal
          onClose={() => setShowAddCandidate(false)}
          onSubmit={handleAddCandidate}
          isLoading={createCandidate.isPending}
        />
      )}
    </div>
  );
}

function CandidateRow({
  candidate,
  onHire,
  onReject,
}: {
  candidate: CandidateListItem;
  onHire: () => void;
  onReject: () => void;
}) {
  const isTerminal = candidate.stage === 'HIRED' || candidate.stage === 'REJECTED';
  return (
    <tr className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
      <td className="px-4 py-3 font-medium text-slate-900">{candidate.full_name}</td>
      <td className="px-4 py-3 text-slate-600">{candidate.phone}</td>
      <td className="px-4 py-3">
        <span
          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${CANDIDATE_STAGE_COLORS[candidate.stage] ?? ''}`}
        >
          {CANDIDATE_STAGE_LABELS[candidate.stage] ?? candidate.stage}
        </span>
      </td>
      <td className="px-4 py-3 text-slate-600">{candidate.source}</td>
      <td className="px-4 py-3 text-slate-600">{candidate.applied_at}</td>
      <td className="px-4 py-3 text-right">
        {!isTerminal && (
          <div className="flex items-center justify-end gap-2">
            <button
              onClick={onHire}
              className="flex items-center gap-1 px-3 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 rounded hover:bg-emerald-200 transition-colors"
            >
              <UserCheck className="h-3 w-3" />
              Нанять
            </button>
            <button
              onClick={onReject}
              className="flex items-center gap-1 px-3 py-1 text-xs font-medium bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
            >
              <UserX className="h-3 w-3" />
              Отклонить
            </button>
          </div>
        )}
      </td>
    </tr>
  );
}

function AddCandidateModal({
  onClose,
  onSubmit,
  isLoading,
}: {
  onClose: () => void;
  onSubmit: (data: Omit<CreateCandidateData, 'vacancy'>) => void;
  isLoading: boolean;
}) {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [source, setSource] = useState<CandidateSource>('EXTERNAL');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!firstName || !lastName || !phone) return;
    onSubmit({ first_name: firstName, last_name: lastName, phone, source });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-md w-full max-w-md p-6 space-y-4">
        <h2 className="text-lg font-semibold font-heading text-slate-900">Добавить кандидата</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Имя</label>
              <input
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Фамилия</label>
              <input
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Телефон</label>
            <input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="+998..."
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Источник</label>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value as CandidateSource)}
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="EXTERNAL">Внешний</option>
              <option value="INTERNAL">Внутренний</option>
              <option value="REFERRAL">Рекомендация</option>
              <option value="HEMIS">HEMIS</option>
            </select>
          </div>
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200 transition-colors"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Добавление...' : 'Добавить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
