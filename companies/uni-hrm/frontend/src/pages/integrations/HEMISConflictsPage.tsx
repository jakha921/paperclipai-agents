import { useState } from 'react';
import { useSyncConflicts, useResolveConflict } from '@/features/hemis/hooks';

type FilterState = 'all' | 'unresolved' | 'resolved';

export default function HEMISConflictsPage() {
  const [filter, setFilter] = useState<FilterState>('unresolved');
  const resolvedParam = filter === 'all' ? null : filter === 'resolved';

  const { data: conflicts, isLoading } = useSyncConflicts(resolvedParam);
  const resolveMutation = useResolveConflict();

  const handleResolve = (id: string, resolution: 'local' | 'hemis') => {
    resolveMutation.mutate({ id, data: { resolution } });
  };

  const filterTabs: { key: FilterState; label: string }[] = [
    { key: 'all', label: 'Все' },
    { key: 'unresolved', label: 'Нерешённые' },
    { key: 'resolved', label: 'Решённые' },
  ];

  return (
    <div className="p-6 space-y-6">
      <h1
        className="text-2xl font-bold text-slate-900"
        style={{ fontFamily: 'var(--font-heading)' }}
      >
        Конфликты синхронизации
      </h1>

      {/* Filter Tabs */}
      <div className="flex gap-1 bg-slate-100 p-1 rounded-lg w-fit">
        {filterTabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setFilter(tab.key)}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${
              filter === tab.key
                ? 'bg-white text-slate-900 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Conflicts Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6">Загрузка...</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Поле</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Объект</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">
                  Локальное значение
                </th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Значение HEMIS</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Статус</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(conflicts ?? []).map((conflict) => (
                <tr key={conflict.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-xs text-slate-600">
                    {conflict.field_name}
                  </td>
                  <td className="px-4 py-3 text-slate-500 text-xs">
                    {conflict.mapping.content_type}: {conflict.mapping.local_id}
                  </td>
                  <td className="px-4 py-3 text-slate-900">{conflict.local_value}</td>
                  <td className="px-4 py-3 text-slate-900">{conflict.hemis_value}</td>
                  <td className="px-4 py-3">
                    {conflict.is_resolved ? (
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-700">
                        {conflict.resolution === 'local' ? 'Локальное' : 'HEMIS'}
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700">
                        Нерешён
                      </span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {!conflict.is_resolved && (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleResolve(conflict.id, 'local')}
                          disabled={resolveMutation.isPending}
                          className="text-xs px-2 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded transition-colors"
                        >
                          Оставить локальное
                        </button>
                        <button
                          onClick={() => handleResolve(conflict.id, 'hemis')}
                          disabled={resolveMutation.isPending}
                          className="text-xs px-2 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded transition-colors"
                        >
                          Принять из HEMIS
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {!isLoading && conflicts?.length === 0 && (
          <div className="text-center py-12 text-slate-500">Нет конфликтов</div>
        )}
      </div>
    </div>
  );
}
