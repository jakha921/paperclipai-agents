import { useState } from 'react';
import { BarChart3 } from 'lucide-react';
import { useTimeSheets, useSubmitTimeSheet, useApproveTimeSheet } from '@/features/attendance/api';
import type { TimesheetStatus } from '@/features/attendance/types';
import {
  Button,
  Card,
  CardContent,
  PageHeader,
  Badge,
  EmptyState,
  Skeleton,
} from '@/shared/ui';

const STATUS_LABELS: Record<TimesheetStatus, string> = {
  DRAFT: 'Черновик',
  SUBMITTED: 'На проверке',
  APPROVED: 'Утверждён',
};

const STATUS_VARIANTS: Record<TimesheetStatus, 'default' | 'warning' | 'success'> = {
  DRAFT: 'default',
  SUBMITTED: 'warning',
  APPROVED: 'success',
};

const MONTHS = [
  'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь',
];

export default function TimesheetPage() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());

  const { data: timesheets, isLoading } = useTimeSheets({ month, year });
  const submitTimeSheet = useSubmitTimeSheet();
  const approveTimeSheet = useApproveTimeSheet();

  return (
    <div className="p-6 space-y-6">
      <PageHeader title="Табель посещаемости" description="Сводные данные по посещаемости" />

      <Card className="p-4">
        <div className="flex flex-wrap gap-3">
          <select
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
            className="px-3 py-2 rounded-md border border-slate-200 text-sm text-slate-600"
          >
            {MONTHS.map((m, i) => (
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
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !timesheets || timesheets.length === 0 ? (
            <EmptyState
              icon={<BarChart3 className="h-12 w-12 text-slate-300" />}
              title="Нет данных"
              description="Табели за выбранный период не найдены"
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Сотрудник</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Рабочих дней</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Присутствовал</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Отсутствовал</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Опоздал</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">В отпуске</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Часы</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Сверхурочные</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Статус</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {timesheets.map((ts) => (
                    <tr key={ts.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-3 px-4 text-sm font-medium text-slate-700">{ts.employee}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{ts.total_working_days}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{ts.days_present}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{ts.days_absent}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{ts.days_late}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{ts.days_on_leave}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{ts.total_hours}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{ts.overtime_hours}</td>
                      <td className="py-3 px-4">
                        <Badge variant={STATUS_VARIANTS[ts.status]}>
                          {STATUS_LABELS[ts.status]}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-2">
                          {ts.status === 'DRAFT' && (
                            <Button
                              size="sm"
                              variant="secondary"
                              loading={submitTimeSheet.isPending}
                              onClick={() => submitTimeSheet.mutate(ts.id)}
                            >
                              Отправить
                            </Button>
                          )}
                          {ts.status === 'SUBMITTED' && (
                            <Button
                              size="sm"
                              loading={approveTimeSheet.isPending}
                              onClick={() => approveTimeSheet.mutate(ts.id)}
                            >
                              Утвердить
                            </Button>
                          )}
                        </div>
                      </td>
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
