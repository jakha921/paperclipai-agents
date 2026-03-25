import { useEmployeeAppraisals, useCompleteAppraisal } from '@/features/appraisal/api';
import {
  EMPLOYEE_APPRAISAL_STATUS_LABELS,
  EMPLOYEE_APPRAISAL_STATUS_COLORS,
} from '@/shared/constants/statuses';
import { cn } from '@/shared/lib/utils';

export default function ReviewPage() {
  const { data, isLoading } = useEmployeeAppraisals({ status: 'self_review' });
  const { mutate: complete, isPending } = useCompleteAppraisal();

  const appraisals = data?.results ?? [];

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1
          className="text-2xl font-bold text-slate-900"
          style={{ fontFamily: 'var(--font-heading)' }}
        >
          Оценка сотрудников
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">Аттестации ожидающие оценки руководителя</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6 space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 bg-slate-100 rounded animate-pulse" />
            ))}
          </div>
        ) : appraisals.length === 0 ? (
          <div className="flex items-center justify-center py-16 text-slate-400">
            <p>Нет аттестаций для оценки</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100">
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                  Сотрудник
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                  Цикл
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                  Статус
                </th>
                <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                  Балл
                </th>
                <th className="px-6 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {appraisals.map((a) => (
                <tr key={a.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-slate-900">
                    {a.employee_name ?? a.employee}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    {a.cycle_name ?? a.cycle}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={cn(
                        'inline-flex px-2 py-0.5 rounded-full text-xs font-medium',
                        EMPLOYEE_APPRAISAL_STATUS_COLORS[a.status] ?? 'bg-slate-100 text-slate-600',
                      )}
                    >
                      {EMPLOYEE_APPRAISAL_STATUS_LABELS[a.status] ?? a.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">
                    {a.overall_score ? parseFloat(a.overall_score).toFixed(1) : '—'}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => complete(a.id)}
                      disabled={isPending}
                      className="px-3 py-1.5 text-xs font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                    >
                      Завершить
                    </button>
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
