import { useState } from 'react';
import { CalendarDays, Plus } from 'lucide-react';
import { useLeaveBalance, useLeaveRequests, useSubmitLeave, useCancelLeave } from '@/features/leaves/api';
import type { LeaveStatus } from '@/features/leaves/types';
import {
  Button,
  Card,
  CardContent,
  PageHeader,
  Badge,
  EmptyState,
  Skeleton,
} from '@/shared/ui';
import { cn } from '@/shared/lib/utils';
import { LeaveRequestModal } from './LeaveRequestModal';

const STATUS_LABELS: Record<LeaveStatus, string> = {
  DRAFT: 'Черновик',
  PENDING_HEAD: 'На согласовании (рук.)',
  PENDING_HR: 'На согласовании (HR)',
  APPROVED: 'Одобрено',
  REJECTED: 'Отклонено',
  CANCELLED: 'Отменено',
};

const STATUS_VARIANTS: Record<LeaveStatus, 'default' | 'success' | 'warning' | 'error' | 'info'> = {
  DRAFT: 'default',
  PENDING_HEAD: 'warning',
  PENDING_HR: 'warning',
  APPROVED: 'success',
  REJECTED: 'error',
  CANCELLED: 'default',
};

export default function MyLeavesPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const { data: balances, isLoading: balanceLoading } = useLeaveBalance();
  const { data: requests, isLoading: requestsLoading } = useLeaveRequests();
  const submitLeave = useSubmitLeave();
  const cancelLeave = useCancelLeave();

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Мои отпуска"
        description="Баланс отпусков и заявки"
        actions={
          <Button onClick={() => setModalOpen(true)}>
            <Plus className="h-4 w-4 mr-2" /> Подать заявку
          </Button>
        }
      />

      {/* Balance cards */}
      {balanceLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full" />
          ))}
        </div>
      ) : balances && balances.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {balances.map((b) => {
            const usedPercent =
              b.total_days > 0 ? Math.round((b.used_days / b.total_days) * 100) : 0;
            return (
              <Card key={b.leave_type.id} className="p-4">
                <p className="text-sm font-medium text-slate-600 truncate">
                  {b.leave_type.name.ru || b.leave_type.code}
                </p>
                <div className="mt-3 flex items-end gap-2">
                  <span className="text-3xl font-bold text-slate-900">{b.remaining_days}</span>
                  <span className="text-sm text-slate-500 pb-1">из {b.total_days} дней</span>
                </div>
                <div className="mt-3 h-2 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className={cn(
                      'h-full rounded-full transition-all',
                      usedPercent > 80 ? 'bg-red-500' : usedPercent > 50 ? 'bg-amber-500' : 'bg-indigo-500',
                    )}
                    style={{ width: `${usedPercent}%` }}
                  />
                </div>
                <p className="mt-1 text-xs text-slate-400">
                  Использовано: {b.used_days} | Перенос: {b.carry_over_days}
                </p>
              </Card>
            );
          })}
        </div>
      ) : null}

      {/* Requests table */}
      <Card>
        <CardContent>
          {requestsLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !requests || requests.length === 0 ? (
            <EmptyState
              icon={<CalendarDays className="h-12 w-12 text-slate-300" />}
              title="Нет заявок"
              description="Подайте первую заявку на отпуск"
              action={
                <Button onClick={() => setModalOpen(true)}>Подать заявку</Button>
              }
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Тип</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Начало</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Конец</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Дней</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Статус</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.map((req) => (
                    <tr key={req.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-3 px-4 text-sm text-slate-700">
                        {req.leave_type.name.ru || req.leave_type.code}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-600">{req.start_date}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{req.end_date}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{req.days_count}</td>
                      <td className="py-3 px-4">
                        <Badge variant={STATUS_VARIANTS[req.status]}>
                          {STATUS_LABELS[req.status]}
                        </Badge>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-2">
                          {req.status === 'DRAFT' && (
                            <Button
                              size="sm"
                              variant="secondary"
                              loading={submitLeave.isPending}
                              onClick={() => submitLeave.mutate(req.id)}
                            >
                              Отправить
                            </Button>
                          )}
                          {(req.status === 'DRAFT' || req.status === 'PENDING_HEAD') && (
                            <Button
                              size="sm"
                              variant="ghost"
                              loading={cancelLeave.isPending}
                              onClick={() => cancelLeave.mutate(req.id)}
                            >
                              Отменить
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

      <LeaveRequestModal isOpen={modalOpen} onClose={() => setModalOpen(false)} />
    </div>
  );
}
