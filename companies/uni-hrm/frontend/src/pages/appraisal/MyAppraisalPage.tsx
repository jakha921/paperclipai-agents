import { useState } from 'react';
import { useAppraisalCycles, useEmployeeAppraisals, useSelfReview } from '@/features/appraisal/api';
import {
  EMPLOYEE_APPRAISAL_STATUS_LABELS,
  EMPLOYEE_APPRAISAL_STATUS_COLORS,
} from '@/shared/constants/statuses';
import { cn } from '@/shared/lib/utils';

export default function MyAppraisalPage() {
  const [selectedCycle, setSelectedCycle] = useState('');
  const { data: cyclesData } = useAppraisalCycles();
  const { data: appraisalsData } = useEmployeeAppraisals(
    selectedCycle ? { cycle: selectedCycle } : undefined,
  );
  const { mutate: startSelfReview, isPending } = useSelfReview();

  const cycles = cyclesData?.results ?? [];
  const appraisals = appraisalsData?.results ?? [];
  const currentAppraisal = appraisals[0];

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="mb-6">
        <h1
          className="text-2xl font-bold text-slate-900"
          style={{ fontFamily: 'var(--font-heading)' }}
        >
          Моя аттестация
        </h1>
      </div>

      {/* Cycle selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-slate-700 mb-1">Цикл аттестации</label>
        <select
          value={selectedCycle}
          onChange={(e) => setSelectedCycle(e.target.value)}
          className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="">Выберите цикл...</option>
          {cycles.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {selectedCycle && !currentAppraisal && (
        <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-400">
          <p>Аттестация для выбранного цикла не найдена</p>
        </div>
      )}

      {currentAppraisal && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-semibold text-slate-900">Текущая аттестация</h2>
              <p className="text-sm text-slate-500 mt-0.5">
                Цикл: {currentAppraisal.cycle_name ?? currentAppraisal.cycle}
              </p>
            </div>
            <span
              className={cn(
                'inline-flex px-3 py-1 rounded-full text-xs font-medium',
                EMPLOYEE_APPRAISAL_STATUS_COLORS[currentAppraisal.status] ??
                  'bg-slate-100 text-slate-600',
              )}
            >
              {EMPLOYEE_APPRAISAL_STATUS_LABELS[currentAppraisal.status] ?? currentAppraisal.status}
            </span>
          </div>

          {currentAppraisal.overall_score && (
            <div className="mb-4 p-4 bg-indigo-50 rounded-lg">
              <p className="text-sm font-medium text-indigo-700">Итоговый балл</p>
              <p className="text-3xl font-bold text-indigo-900 mt-1">
                {parseFloat(currentAppraisal.overall_score).toFixed(1)}
                <span className="text-base font-normal text-indigo-600"> / 10</span>
              </p>
            </div>
          )}

          {currentAppraisal.status === 'pending' && (
            <button
              onClick={() => startSelfReview(currentAppraisal.id)}
              disabled={isPending}
              className="w-full py-2 bg-indigo-600 text-white text-sm font-medium rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              Начать самооценку
            </button>
          )}

          {currentAppraisal.comments && (
            <div className="mt-4 p-3 bg-slate-50 rounded-lg">
              <p className="text-xs font-medium text-slate-500 mb-1">Комментарий</p>
              <p className="text-sm text-slate-700">{currentAppraisal.comments}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
