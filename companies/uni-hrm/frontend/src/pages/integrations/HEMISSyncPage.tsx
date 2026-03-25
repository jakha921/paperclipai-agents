import { useSyncLogs, useHEMISStatus, useRunSync } from '@/features/hemis/hooks';
import type { SyncLog } from '@/features/hemis/types';
import { Link } from 'react-router-dom';
import { RefreshCw } from 'lucide-react';

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    running: 'bg-blue-50 text-blue-700',
    success: 'bg-green-50 text-green-700',
    error: 'bg-red-50 text-red-700',
    never_synced: 'bg-slate-100 text-slate-500',
  };
  const labels: Record<string, string> = {
    running: 'Выполняется',
    success: 'Успешно',
    error: 'Ошибка',
    never_synced: 'Не синхронизировано',
  };
  return (
    <span
      className={`px-2 py-0.5 rounded-full text-xs font-medium ${styles[status] ?? styles.never_synced}`}
    >
      {labels[status] ?? status}
    </span>
  );
}

function SyncTypeLabel({ type }: { type: string }) {
  const labels: Record<string, string> = {
    departments: 'Отделы',
    employees: 'Сотрудники',
    academic: 'Нагрузка',
    full: 'Полная',
  };
  return <span>{labels[type] ?? type}</span>;
}

function isSyncLog(data: unknown): data is SyncLog {
  return typeof data === 'object' && data !== null && 'sync_type' in data;
}

export default function HEMISSyncPage() {
  const { data: statusData } = useHEMISStatus();
  const { data: logs } = useSyncLogs();
  const syncMutation = useRunSync();

  const lastLog = isSyncLog(statusData) ? statusData : null;
  const recentLogs = (logs ?? []).slice(0, 10);

  const handleSync = (syncType: 'departments' | 'employees' | 'full') => {
    syncMutation.mutate({ sync_type: syncType });
  };

  const getStatValue = (key: 'created' | 'updated'): number => {
    if (!lastLog?.stats) return 0;
    if (typeof lastLog.stats === 'object' && key in lastLog.stats) {
      const stats = lastLog.stats as { created?: number; updated?: number };
      return stats[key] ?? 0;
    }
    return 0;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1
          className="text-2xl font-bold text-slate-900"
          style={{ fontFamily: 'var(--font-heading)' }}
        >
          HEMIS Синхронизация
        </h1>
        <Link
          to="/integrations/hemis/conflicts"
          className="text-sm font-medium text-indigo-600 hover:text-indigo-700"
        >
          Конфликты
        </Link>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
          <p className="text-xs font-medium text-slate-500">Статус</p>
          <div className="mt-2">
            <StatusBadge status={lastLog?.status ?? 'never_synced'} />
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
          <p className="text-xs font-medium text-slate-500">Последняя синхронизация</p>
          <p className="text-sm font-semibold text-slate-900 mt-1">
            {lastLog?.started_at
              ? new Date(lastLog.started_at).toLocaleString('ru-RU')
              : 'Никогда'}
          </p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
          <p className="text-xs font-medium text-slate-500">Создано</p>
          <p className="text-2xl font-bold text-indigo-600 mt-1">{getStatValue('created')}</p>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
          <p className="text-xs font-medium text-slate-500">Обновлено</p>
          <p className="text-2xl font-bold text-slate-900 mt-1">{getStatValue('updated')}</p>
        </div>
      </div>

      {/* Sync Buttons */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => handleSync('departments')}
          disabled={syncMutation.isPending}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Синхр. отделы
        </button>
        <button
          onClick={() => handleSync('employees')}
          disabled={syncMutation.isPending}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Синхр. сотрудников
        </button>
        <button
          onClick={() => handleSync('full')}
          disabled={syncMutation.isPending}
          className="flex items-center gap-2 bg-indigo-800 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-900 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Полная синхр.
        </button>
        {syncMutation.isPending && (
          <span className="text-sm text-slate-500 self-center">Запускаем синхронизацию...</span>
        )}
      </div>

      {/* Sync Logs Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-4 py-3 border-b border-slate-200">
          <h2 className="text-base font-semibold text-slate-900">История синхронизаций</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Тип</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Начало</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Завершение</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Статус</th>
              <th className="text-left px-4 py-3 font-medium text-slate-600">Результат</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {recentLogs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 font-medium text-slate-900">
                  <SyncTypeLabel type={log.sync_type} />
                </td>
                <td className="px-4 py-3 text-slate-500">
                  {new Date(log.started_at).toLocaleString('ru-RU')}
                </td>
                <td className="px-4 py-3 text-slate-500">
                  {log.completed_at
                    ? new Date(log.completed_at).toLocaleString('ru-RU')
                    : '\u2014'}
                </td>
                <td className="px-4 py-3">
                  <StatusBadge status={log.status} />
                </td>
                <td className="px-4 py-3 text-slate-500 text-xs font-mono">
                  {JSON.stringify(log.stats)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {recentLogs.length === 0 && (
          <div className="text-center py-12 text-slate-500">Нет истории синхронизаций</div>
        )}
      </div>
    </div>
  );
}
