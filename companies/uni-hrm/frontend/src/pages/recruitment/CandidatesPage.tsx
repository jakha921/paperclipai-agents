import { useState } from 'react';
import { Users, UserCheck, UserX } from 'lucide-react';
import { useCandidates, useHireCandidate, useRejectCandidate } from '@/features/recruitment';
import type { CandidateStage } from '@/features/recruitment';
import {
  CANDIDATE_STAGE_COLORS,
  CANDIDATE_STAGE_LABELS,
  CANDIDATE_SOURCE_LABELS,
} from '@/shared/constants/statuses';

const STAGE_OPTIONS: Array<{ value: CandidateStage | ''; label: string }> = [
  { value: '', label: 'Все стадии' },
  { value: 'APPLIED', label: 'Заявка' },
  { value: 'SCREENING', label: 'Проверка' },
  { value: 'INTERVIEW', label: 'Интервью' },
  { value: 'OFFER', label: 'Предложение' },
  { value: 'HIRED', label: 'Принят' },
  { value: 'REJECTED', label: 'Отклонён' },
];

export default function CandidatesPage() {
  const [stageFilter, setStageFilter] = useState<CandidateStage | ''>('');
  const params = stageFilter ? { stage: stageFilter } : undefined;

  const { data, isLoading } = useCandidates(params);
  const hireCandidate = useHireCandidate();
  const rejectCandidate = useRejectCandidate();

  const candidates = data?.results ?? [];

  const handleHire = async (id: string) => {
    const result = await hireCandidate.mutateAsync(id);
    alert(`Сотрудник создан. ID: ${result.employee_id}`);
  };

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-14 bg-slate-200 animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold font-heading text-slate-900">Кандидаты</h1>
        <p className="text-sm text-slate-500 mt-1">{data?.count ?? 0} кандидатов</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {STAGE_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setStageFilter(opt.value)}
            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
              stageFilter === opt.value
                ? 'bg-indigo-600 text-white'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {candidates.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <Users className="h-12 w-12 mb-3" />
            <p className="text-sm font-medium">Кандидатов нет</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="text-left px-4 py-3 font-medium text-slate-600">Кандидат</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Вакансия</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Телефон</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Стадия</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Источник</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Дата заявки</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">Действия</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((c) => {
                const isTerminal = c.stage === 'HIRED' || c.stage === 'REJECTED';
                return (
                  <tr
                    key={c.id}
                    className="border-b border-slate-100 hover:bg-slate-50 transition-colors"
                  >
                    <td className="px-4 py-3 font-medium text-slate-900">{c.full_name}</td>
                    <td className="px-4 py-3 text-slate-600">{c.vacancy_title}</td>
                    <td className="px-4 py-3 text-slate-600">{c.phone}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${CANDIDATE_STAGE_COLORS[c.stage] ?? ''}`}
                      >
                        {CANDIDATE_STAGE_LABELS[c.stage] ?? c.stage}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {CANDIDATE_SOURCE_LABELS[c.source] ?? c.source}
                    </td>
                    <td className="px-4 py-3 text-slate-600">{c.applied_at}</td>
                    <td className="px-4 py-3 text-right">
                      {!isTerminal && (
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleHire(c.id)}
                            disabled={hireCandidate.isPending}
                            className="flex items-center gap-1 px-3 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 rounded hover:bg-emerald-200 transition-colors disabled:opacity-50"
                          >
                            <UserCheck className="h-3 w-3" />
                            Нанять
                          </button>
                          <button
                            onClick={() => rejectCandidate.mutate(c.id)}
                            disabled={rejectCandidate.isPending}
                            className="flex items-center gap-1 px-3 py-1 text-xs font-medium bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors disabled:opacity-50"
                          >
                            <UserX className="h-3 w-3" />
                            Отклонить
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
