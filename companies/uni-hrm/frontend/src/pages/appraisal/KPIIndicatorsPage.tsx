import { useKPIIndicators } from '@/features/appraisal/api';
import { KPI_CATEGORY_LABELS } from '@/shared/constants/statuses';
import type { KPIIndicator } from '@/features/appraisal/types';

function groupByCategory(items: KPIIndicator[]): Record<string, KPIIndicator[]> {
  return items.reduce(
    (acc, item) => {
      const cat = item.category;
      if (!acc[cat]) acc[cat] = [];
      acc[cat].push(item);
      return acc;
    },
    {} as Record<string, KPIIndicator[]>,
  );
}

export default function KPIIndicatorsPage() {
  const { data, isLoading } = useKPIIndicators();
  const indicators = data?.results ?? [];
  const grouped = groupByCategory(indicators);

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1
          className="text-2xl font-bold text-slate-900"
          style={{ fontFamily: 'var(--font-heading)' }}
        >
          KPI Индикаторы
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">{data?.count ?? 0} показателей</p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map((i) => (
            <div key={i} className="h-32 bg-slate-100 rounded-xl animate-pulse" />
          ))}
        </div>
      ) : indicators.length === 0 ? (
        <div className="flex items-center justify-center py-16 text-slate-400 bg-white rounded-xl border border-slate-200">
          <p>Нет KPI индикаторов</p>
        </div>
      ) : (
        <div className="space-y-6">
          {Object.entries(grouped).map(([category, items]) => (
            <div key={category} className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="px-6 py-3 bg-slate-50 border-b border-slate-100">
                <h2 className="text-sm font-semibold text-slate-700">
                  {KPI_CATEGORY_LABELS[category] ?? category}
                </h2>
              </div>
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                      Название
                    </th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                      Вес
                    </th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">
                      Макс. балл
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {items.map((kpi) => (
                    <tr key={kpi.id} className="hover:bg-slate-50">
                      <td className="px-6 py-3 text-sm text-slate-900">
                        {kpi.name['ru'] ?? kpi.name['en'] ?? '—'}
                      </td>
                      <td className="px-6 py-3 text-sm text-slate-600">{kpi.weight}%</td>
                      <td className="px-6 py-3 text-sm text-slate-600">{kpi.max_score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
