import { useState } from 'react';
import { useTrainingRecords } from '@/features/appraisal/api';
import {
  TRAINING_STATUS_LABELS,
  TRAINING_STATUS_COLORS,
} from '@/shared/constants/statuses';
import type { TrainingStatus } from '@/features/appraisal/types';
import { cn } from '@/shared/lib/utils';

type FilterTab = 'all' | TrainingStatus;

function formatDate(d: string | null) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('ru-RU');
}

export default function MyCoursesPage() {
  const [filter, setFilter] = useState<FilterTab>('all');
  const { data, isLoading } = useTrainingRecords();

  const records = (data?.results ?? []).filter(
    (r) => filter === 'all' || r.status === filter,
  );

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1
          className="text-2xl font-bold text-slate-900"
          style={{ fontFamily: 'var(--font-heading)' }}
        >
          Мои курсы
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">{data?.count ?? 0} записей</p>
      </div>

      {/* Filter */}
      <div className="flex gap-1 p-1 bg-slate-100 rounded-lg mb-6 w-fit flex-wrap">
        {(['all', 'enrolled', 'in_progress', 'completed', 'cancelled'] as FilterTab[]).map(
          (t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={cn(
                'px-3 py-1.5 text-sm font-medium rounded-md transition-colors',
                filter === t
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-500 hover:text-slate-700',
              )}
            >
              {t === 'all' ? 'Все' : (TRAINING_STATUS_LABELS[t] ?? t)}
            </button>
          ),
        )}
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-10 bg-slate-100 rounded animate-pulse" />
            ))}
          </div>
        ) : records.length === 0 ? (
          <div className="flex items-center justify-center py-16 text-slate-400">
            <p>Нет записей об обучении</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                  Программа
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                  Период
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                  Статус
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                  Сертификат
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                  Балл
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {records.map((r) => (
                <tr key={r.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-slate-900">
                    {r.program_name?.['ru'] ?? r.program_name?.['en'] ?? r.program}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    {formatDate(r.start_date)} — {formatDate(r.end_date)}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={cn(
                        'inline-flex px-2 py-0.5 rounded-full text-xs font-medium',
                        TRAINING_STATUS_COLORS[r.status] ?? 'bg-slate-100 text-slate-600',
                      )}
                    >
                      {TRAINING_STATUS_LABELS[r.status] ?? r.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    {r.certificate_number || '—'}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    {r.score ?? '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
