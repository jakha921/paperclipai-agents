import { useState, useMemo } from 'react';
import { CalendarRange } from 'lucide-react';
import { useLeaveCalendar } from '@/features/leaves/api';
import { Card, CardContent, PageHeader, EmptyState, Skeleton } from '@/shared/ui';
import { cn } from '@/shared/lib/utils';

const LEAVE_COLORS: Record<string, string> = {
  ANNUAL_PPS: 'bg-indigo-400',
  ANNUAL_AUP: 'bg-blue-400',
  SICK: 'bg-red-400',
  MATERNITY: 'bg-pink-400',
  UNPAID: 'bg-slate-400',
  STUDY: 'bg-emerald-400',
};

const MONTHS = [
  { value: '1', label: 'Январь' },
  { value: '2', label: 'Февраль' },
  { value: '3', label: 'Март' },
  { value: '4', label: 'Апрель' },
  { value: '5', label: 'Май' },
  { value: '6', label: 'Июнь' },
  { value: '7', label: 'Июль' },
  { value: '8', label: 'Август' },
  { value: '9', label: 'Сентябрь' },
  { value: '10', label: 'Октябрь' },
  { value: '11', label: 'Ноябрь' },
  { value: '12', label: 'Декабрь' },
];

function getDaysInMonth(month: number, year: number): number {
  return new Date(year, month, 0).getDate();
}

export default function LeaveCalendarPage() {
  const now = new Date();
  const [month, setMonth] = useState(String(now.getMonth() + 1));
  const [year, setYear] = useState(String(now.getFullYear()));
  const [department, setDepartment] = useState('');

  const { data: events, isLoading } = useLeaveCalendar({
    month,
    year,
    department: department || undefined,
  });

  const daysCount = getDaysInMonth(Number(month), Number(year));

  const employeeRows = useMemo(() => {
    if (!events || events.length === 0) return [];
    const grouped = new Map<string, typeof events>();
    for (const ev of events) {
      const list = grouped.get(ev.employee_name) ?? [];
      list.push(ev);
      grouped.set(ev.employee_name, list);
    }
    return Array.from(grouped.entries()).map(([name, evts]) => ({ name, events: evts }));
  }, [events]);

  const isOnLeave = (evts: typeof events, day: number) => {
    if (!evts) return null;
    const dateStr = `${year}-${month.padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return evts.find((e) => dateStr >= e.start_date && dateStr <= e.end_date) ?? null;
  };

  return (
    <div className="p-6 space-y-6">
      <PageHeader title="Календарь отпусков" description="Визуальное представление отпусков" />

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
            onChange={(e) => setMonth(e.target.value)}
            className="px-3 py-2 rounded-md border border-slate-200 text-sm text-slate-600"
          >
            {MONTHS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
          <input
            type="number"
            value={year}
            onChange={(e) => setYear(e.target.value)}
            min="2020"
            max="2030"
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
              icon={<CalendarRange className="h-12 w-12 text-slate-300" />}
              title="Нет отпусков"
              description="Нет отпусков в этом периоде"
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
                        className="py-2 px-1 text-xs font-medium text-slate-500 border-b border-slate-200 text-center min-w-[28px]"
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
                        const event = isOnLeave(row.events, i + 1);
                        return (
                          <td
                            key={i}
                            className="py-2 px-0.5 border-b border-slate-50 text-center"
                            title={event ? `${event.leave_type} (${event.status})` : ''}
                          >
                            {event && (
                              <div
                                className={cn(
                                  'h-5 w-5 mx-auto rounded-sm',
                                  LEAVE_COLORS[event.leave_type] ?? 'bg-indigo-300',
                                )}
                              />
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
    </div>
  );
}
