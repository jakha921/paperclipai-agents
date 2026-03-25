import { useState, useMemo } from 'react';
import { ClipboardList } from 'lucide-react';
import { useAttendanceRecords } from '@/features/attendance/api';
import type { AttendanceStatus } from '@/features/attendance/types';
import { Card, CardContent, PageHeader, EmptyState, Skeleton } from '@/shared/ui';
import { cn } from '@/shared/lib/utils';

const STATUS_DISPLAY: Record<AttendanceStatus, { symbol: string; color: string; label: string }> = {
  PRESENT: { symbol: '\u2713', color: 'bg-emerald-100 text-emerald-700', label: 'Присутствует' },
  ABSENT: { symbol: '\u2717', color: 'bg-red-100 text-red-700', label: 'Отсутствует' },
  LATE: { symbol: '!', color: 'bg-amber-100 text-amber-700', label: 'Опоздание' },
  HALF_DAY: { symbol: '\u00BD', color: 'bg-orange-100 text-orange-700', label: 'Полдня' },
  ON_LEAVE: { symbol: '\u25CB', color: 'bg-blue-100 text-blue-700', label: 'В отпуске' },
  HOLIDAY: { symbol: '\u2014', color: 'bg-slate-100 text-slate-500', label: 'Выходной' },
};

function getDaysInMonth(month: number, year: number): number {
  return new Date(year, month, 0).getDate();
}

export default function AttendancePage() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [department, setDepartment] = useState('');

  const dateFrom = `${year}-${String(month).padStart(2, '0')}-01`;
  const dateTo = `${year}-${String(month).padStart(2, '0')}-${String(getDaysInMonth(month, year)).padStart(2, '0')}`;

  const { data: records, isLoading } = useAttendanceRecords({
    date_from: dateFrom,
    date_to: dateTo,
    department: department || undefined,
  });

  const daysCount = getDaysInMonth(month, year);

  const employeeRows = useMemo(() => {
    if (!records || records.length === 0) return [];
    const grouped = new Map<string, Map<number, typeof records[0]>>();
    for (const rec of records) {
      const day = new Date(rec.date).getDate();
      if (!grouped.has(rec.employee)) {
        grouped.set(rec.employee, new Map());
      }
      grouped.get(rec.employee)!.set(day, rec);
    }
    return Array.from(grouped.entries()).map(([name, dayMap]) => ({ name, dayMap }));
  }, [records]);

  const MONTHS_OPTIONS = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
  ];

  return (
    <div className="p-6 space-y-6">
      <PageHeader title="Журнал посещаемости" description="Ежедневный учет посещаемости" />

      <Card className="p-4">
        <div className="flex flex-wrap gap-3">
          <input
            type="text"
            placeholder="Подразделение..."
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            className="px-3 py-2 rounded-md border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <select
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
            className="px-3 py-2 rounded-md border border-slate-200 text-sm text-slate-600"
          >
            {MONTHS_OPTIONS.map((m, i) => (
              <option key={i} value={i + 1}>
                {m}
              </option>
            ))}
          </select>
          <input
            type="number"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            min={2020}
            max={2030}
            className="w-24 px-3 py-2 rounded-md border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </Card>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : employeeRows.length === 0 ? (
            <EmptyState
              icon={<ClipboardList className="h-12 w-12 text-slate-300" />}
              title="Нет данных"
              description="Нет записей посещаемости за выбранный период"
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr>
                    <th className="sticky left-0 z-10 bg-white text-left py-2 px-3 text-xs font-medium text-slate-500 uppercase border-b border-r border-slate-200 min-w-[160px]">
                      Сотрудник
                    </th>
                    {Array.from({ length: daysCount }, (_, i) => (
                      <th
                        key={i}
                        className="py-2 px-1 text-xs font-medium text-slate-500 border-b border-slate-200 text-center min-w-[32px]"
                      >
                        {i + 1}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {employeeRows.map((row) => (
                    <tr key={row.name} className="hover:bg-slate-50">
                      <td className="sticky left-0 z-10 bg-white py-2 px-3 text-sm font-medium text-slate-700 border-b border-r border-slate-100 whitespace-nowrap">
                        {row.name}
                      </td>
                      {Array.from({ length: daysCount }, (_, i) => {
                        const rec = row.dayMap.get(i + 1);
                        const display = rec ? STATUS_DISPLAY[rec.status] : null;
                        return (
                          <td
                            key={i}
                            className="py-2 px-0.5 border-b border-slate-50 text-center"
                            title={display ? `${display.label}${rec?.check_in ? ` (${rec.check_in} - ${rec.check_out ?? '...'})` : ''}` : ''}
                          >
                            {display && (
                              <span
                                className={cn(
                                  'inline-flex items-center justify-center h-6 w-6 rounded text-xs font-bold',
                                  display.color,
                                )}
                              >
                                {display.symbol}
                              </span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-xs text-slate-500">
        {Object.entries(STATUS_DISPLAY).map(([key, val]) => (
          <div key={key} className="flex items-center gap-1.5">
            <span className={cn('inline-flex items-center justify-center h-5 w-5 rounded text-xs font-bold', val.color)}>
              {val.symbol}
            </span>
            {val.label}
          </div>
        ))}
      </div>
    </div>
  );
}
