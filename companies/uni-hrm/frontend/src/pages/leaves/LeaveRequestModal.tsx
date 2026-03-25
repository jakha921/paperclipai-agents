import { useState, useMemo } from 'react';
import { Modal, Button, Textarea } from '@/shared/ui';
import { useLeaveTypes, useCreateLeaveRequest } from '@/features/leaves/api';

interface LeaveRequestModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function LeaveRequestModal({ isOpen, onClose }: LeaveRequestModalProps) {
  const { data: leaveTypes, isLoading: typesLoading } = useLeaveTypes();
  const createRequest = useCreateLeaveRequest();

  const [leaveTypeId, setLeaveTypeId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');

  const daysCount = useMemo(() => {
    if (!startDate || !endDate) return 0;
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diff = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    return diff > 0 ? diff : 0;
  }, [startDate, endDate]);

  const isValid = leaveTypeId && startDate && endDate && daysCount > 0;

  const handleSubmit = async () => {
    if (!isValid) return;
    await createRequest.mutateAsync({
      leave_type_id: leaveTypeId,
      start_date: startDate,
      end_date: endDate,
      reason: reason || undefined,
    });
    setLeaveTypeId('');
    setStartDate('');
    setEndDate('');
    setReason('');
    onClose();
  };

  return (
    <Modal open={isOpen} onClose={onClose} title="Подать заявку на отпуск" size="md">
      <div className="space-y-4">
        <div className="space-y-1">
          <label className="block text-sm font-medium text-slate-700">Тип отпуска</label>
          <select
            value={leaveTypeId}
            onChange={(e) => setLeaveTypeId(e.target.value)}
            className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            disabled={typesLoading}
          >
            <option value="">Выберите тип</option>
            {leaveTypes?.map((lt) => (
              <option key={lt.id} value={lt.id}>
                {lt.name.ru || lt.code}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">Дата начала</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">Дата окончания</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              min={startDate}
              className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>

        {daysCount > 0 && (
          <p className="text-sm text-slate-600">
            Количество дней: <span className="font-semibold text-slate-900">{daysCount}</span>
          </p>
        )}

        <Textarea
          label="Причина (необязательно)"
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          rows={3}
          placeholder="Укажите причину отпуска..."
        />

        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose}>
            Отмена
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!isValid}
            loading={createRequest.isPending}
          >
            Создать заявку
          </Button>
        </div>
      </div>
    </Modal>
  );
}
