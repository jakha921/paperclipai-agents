import { useState } from 'react';
import { CheckCircle } from 'lucide-react';
import { useLeaveRequests, useApproveLeave, useRejectLeave } from '@/features/leaves/api';
import type { LeaveStatus } from '@/features/leaves/types';
import {
  Button,
  Card,
  CardContent,
  PageHeader,
  Badge,
  EmptyState,
  Skeleton,
  Tabs,
} from '@/shared/ui';

const STATUS_VARIANTS: Record<LeaveStatus, 'default' | 'success' | 'warning' | 'error' | 'info'> = {
  DRAFT: 'default',
  PENDING_HEAD: 'warning',
  PENDING_HR: 'warning',
  APPROVED: 'success',
  REJECTED: 'error',
  CANCELLED: 'default',
};

const STATUS_LABELS: Record<LeaveStatus, string> = {
  DRAFT: 'Черновик',
  PENDING_HEAD: 'Ожидает рук.',
  PENDING_HR: 'Ожидает HR',
  APPROVED: 'Одобрено',
  REJECTED: 'Отклонено',
  CANCELLED: 'Отменено',
};

const TABS = [
  { value: 'PENDING_HEAD', label: 'Ожидает руководителя' },
  { value: 'PENDING_HR', label: 'Ожидает HR' },
];

export default function LeaveApprovalPage() {
  const [activeTab, setActiveTab] = useState('PENDING_HEAD');
  const [rejectingId, setRejectingId] = useState<string | null>(null);
  const [rejectionReason, setRejectionReason] = useState('');

  const { data: requests, isLoading } = useLeaveRequests({ status: activeTab });
  const approveLeave = useApproveLeave();
  const rejectLeave = useRejectLeave();

  const handleReject = (id: string) => {
    if (!rejectionReason.trim()) return;
    rejectLeave.mutate(
      { id, rejection_reason: rejectionReason },
      {
        onSuccess: () => {
          setRejectingId(null);
          setRejectionReason('');
        },
      },
    );
  };

  return (
    <div className="p-6 space-y-6">
      <PageHeader title="Согласование отпусков" description="Рассмотрение заявок на отпуск" />

      <Tabs tabs={TABS} activeTab={activeTab} onTabChange={setActiveTab} />

      <Card>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-14 w-full" />
              ))}
            </div>
          ) : !requests || requests.length === 0 ? (
            <EmptyState
              icon={<CheckCircle className="h-12 w-12 text-slate-300" />}
              title="Нет заявок"
              description="Все заявки рассмотрены"
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Сотрудник</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Тип</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Начало</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Конец</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Дней</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Статус</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Создано</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.map((req) => (
                    <tr key={req.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-3 px-4 text-sm font-medium text-slate-700">{req.employee}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">
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
                      <td className="py-3 px-4 text-sm text-slate-500">
                        {new Date(req.created_at).toLocaleDateString('ru-RU')}
                      </td>
                      <td className="py-3 px-4">
                        {rejectingId === req.id ? (
                          <div className="flex items-center gap-2">
                            <input
                              type="text"
                              value={rejectionReason}
                              onChange={(e) => setRejectionReason(e.target.value)}
                              placeholder="Причина отказа..."
                              className="rounded-md border border-slate-300 px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
                            />
                            <Button
                              size="sm"
                              variant="danger"
                              loading={rejectLeave.isPending}
                              onClick={() => handleReject(req.id)}
                            >
                              Отклонить
                            </Button>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => {
                                setRejectingId(null);
                                setRejectionReason('');
                              }}
                            >
                              Отмена
                            </Button>
                          </div>
                        ) : (
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              loading={approveLeave.isPending}
                              onClick={() => approveLeave.mutate(req.id)}
                            >
                              Одобрить
                            </Button>
                            <Button
                              size="sm"
                              variant="danger"
                              onClick={() => setRejectingId(req.id)}
                            >
                              Отклонить
                            </Button>
                          </div>
                        )}
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
