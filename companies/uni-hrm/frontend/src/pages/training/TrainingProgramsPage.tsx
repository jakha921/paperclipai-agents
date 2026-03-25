import { useState } from 'react';
import { BookOpen, Clock, DollarSign } from 'lucide-react';
import { useTrainingPrograms } from '@/features/appraisal/api';
import { TRAINING_TYPE_LABELS } from '@/shared/constants/statuses';
import type { TrainingType } from '@/features/appraisal/types';
import { cn } from '@/shared/lib/utils';

const TYPE_COLORS: Record<string, string> = {
  internal: 'bg-blue-100 text-blue-700',
  external: 'bg-purple-100 text-purple-700',
  online: 'bg-green-100 text-green-700',
};

type FilterType = 'all' | TrainingType;

export default function TrainingProgramsPage() {
  const [filter, setFilter] = useState<FilterType>('all');
  const { data, isLoading } = useTrainingPrograms({ is_active: true });

  const programs = (data?.results ?? []).filter(
    (p) => filter === 'all' || p.training_type === filter,
  );

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1
          className="text-2xl font-bold text-slate-900"
          style={{ fontFamily: 'var(--font-heading)' }}
        >
          Программы обучения
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">{data?.count ?? 0} программ</p>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1 p-1 bg-slate-100 rounded-lg mb-6 w-fit">
        {(['all', 'internal', 'external', 'online'] as FilterType[]).map((t) => (
          <button
            key={t}
            onClick={() => setFilter(t)}
            className={cn(
              'px-4 py-1.5 text-sm font-medium rounded-md transition-colors',
              filter === t
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-500 hover:text-slate-700',
            )}
          >
            {t === 'all' ? 'Все' : (TRAINING_TYPE_LABELS[t] ?? t)}
          </button>
        ))}
      </div>

      {/* Cards */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-40 bg-slate-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : programs.length === 0 ? (
        <div className="flex items-center justify-center py-16 text-slate-400 bg-white rounded-xl border border-slate-200">
          <p>Нет программ обучения</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {programs.map((p) => (
            <div
              key={p.id}
              className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 flex flex-col gap-3"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                  <BookOpen className="h-4 w-4" />
                </div>
                <span
                  className={cn(
                    'inline-flex px-2 py-0.5 rounded-full text-xs font-medium',
                    TYPE_COLORS[p.training_type] ?? 'bg-slate-100 text-slate-600',
                  )}
                >
                  {TRAINING_TYPE_LABELS[p.training_type] ?? p.training_type}
                </span>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-900">
                  {p.name['ru'] ?? p.name['en'] ?? '—'}
                </h3>
                {p.provider && (
                  <p className="text-xs text-slate-500 mt-0.5">{p.provider}</p>
                )}
                {p.description && (
                  <p className="text-xs text-slate-600 mt-1 line-clamp-2">{p.description}</p>
                )}
              </div>

              <div className="flex items-center gap-4 text-xs text-slate-500 mt-auto">
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  {p.duration_hours} ч
                </span>
                {parseFloat(p.cost) > 0 && (
                  <span className="flex items-center gap-1">
                    <DollarSign className="h-3.5 w-3.5" />
                    {parseFloat(p.cost).toLocaleString('ru-RU')} сум
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
