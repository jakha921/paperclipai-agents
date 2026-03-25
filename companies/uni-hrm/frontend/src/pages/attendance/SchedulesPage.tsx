import { useState } from 'react';
import { Clock, Plus, Trash2, Pencil } from 'lucide-react';
import {
  useWorkSchedules,
  useCreateWorkSchedule,
  useUpdateWorkSchedule,
  useDeleteWorkSchedule,
} from '@/features/attendance/api';
import type { WorkSchedule, WorkScheduleCreateData } from '@/features/attendance/types';
import {
  Button,
  Card,
  CardContent,
  PageHeader,
  Modal,
  EmptyState,
  Skeleton,
} from '@/shared/ui';

const SCHEDULE_TYPE_LABELS: Record<string, string> = {
  '5/2': '5/2',
  '6/1': '6/1',
  SHIFT: 'Сменный',
  FLEXIBLE: 'Гибкий',
};

const DAY_LABELS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

interface ScheduleFormData {
  name: string;
  schedule_type: WorkScheduleCreateData['schedule_type'];
  work_start: string;
  work_end: string;
  break_start: string;
  break_end: string;
  working_days: number[];
}

const EMPTY_FORM: ScheduleFormData = {
  name: '',
  schedule_type: '5/2',
  work_start: '09:00',
  work_end: '18:00',
  break_start: '13:00',
  break_end: '14:00',
  working_days: [0, 1, 2, 3, 4],
};

export default function SchedulesPage() {
  const { data: schedules, isLoading } = useWorkSchedules();
  const createSchedule = useCreateWorkSchedule();
  const updateSchedule = useUpdateWorkSchedule();
  const deleteSchedule = useDeleteWorkSchedule();

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [form, setForm] = useState<ScheduleFormData>(EMPTY_FORM);

  const openCreate = () => {
    setEditingId(null);
    setForm(EMPTY_FORM);
    setModalOpen(true);
  };

  const openEdit = (schedule: WorkSchedule) => {
    setEditingId(schedule.id);
    setForm({
      name: schedule.name,
      schedule_type: schedule.schedule_type,
      work_start: schedule.work_start,
      work_end: schedule.work_end,
      break_start: schedule.break_start ?? '',
      break_end: schedule.break_end ?? '',
      working_days: schedule.working_days,
    });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    const payload: WorkScheduleCreateData = {
      name: form.name,
      schedule_type: form.schedule_type,
      work_start: form.work_start,
      work_end: form.work_end,
      break_start: form.break_start || undefined,
      break_end: form.break_end || undefined,
      working_days: form.working_days,
    };

    if (editingId) {
      await updateSchedule.mutateAsync({ id: editingId, data: payload });
    } else {
      await createSchedule.mutateAsync(payload);
    }
    setModalOpen(false);
  };

  const toggleDay = (day: number) => {
    setForm((f) => ({
      ...f,
      working_days: f.working_days.includes(day)
        ? f.working_days.filter((d) => d !== day)
        : [...f.working_days, day].sort(),
    }));
  };

  const isSubmitting = createSchedule.isPending || updateSchedule.isPending;

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Рабочие графики"
        description="Управление графиками работы"
        actions={
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4 mr-2" /> Добавить график
          </Button>
        }
      />

      <Card>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : !schedules || schedules.length === 0 ? (
            <EmptyState
              icon={<Clock className="h-12 w-12 text-slate-300" />}
              title="Нет графиков"
              description="Создайте первый рабочий график"
              action={<Button onClick={openCreate}>Добавить</Button>}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Название</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Тип</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Начало</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Конец</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Перерыв</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Рабочие дни</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {schedules.map((s) => (
                    <tr key={s.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-3 px-4 text-sm font-medium text-slate-700">{s.name}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{SCHEDULE_TYPE_LABELS[s.schedule_type]}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{s.work_start}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{s.work_end}</td>
                      <td className="py-3 px-4 text-sm text-slate-500">
                        {s.break_start && s.break_end ? `${s.break_start} - ${s.break_end}` : '-'}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-600">
                        {s.working_days.map((d) => DAY_LABELS[d]).join(', ')}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-2">
                          <button
                            onClick={() => openEdit(s)}
                            className="text-indigo-600 hover:text-indigo-800"
                            title="Редактировать"
                          >
                            <Pencil className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => deleteSchedule.mutate(s.id)}
                            className="text-red-500 hover:text-red-700"
                            title="Удалить"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
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

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingId ? 'Редактировать график' : 'Новый график'}
        size="md"
      >
        <div className="space-y-4">
          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">Название</label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              placeholder="Стандартный 5/2"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">Тип графика</label>
            <select
              value={form.schedule_type}
              onChange={(e) => setForm((f) => ({ ...f, schedule_type: e.target.value as WorkScheduleCreateData['schedule_type'] }))}
              className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              {Object.entries(SCHEDULE_TYPE_LABELS).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-slate-700">Начало работы</label>
              <input
                type="time"
                value={form.work_start}
                onChange={(e) => setForm((f) => ({ ...f, work_start: e.target.value }))}
                className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div className="space-y-1">
              <label className="block text-sm font-medium text-slate-700">Конец работы</label>
              <input
                type="time"
                value={form.work_end}
                onChange={(e) => setForm((f) => ({ ...f, work_end: e.target.value }))}
                className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-slate-700">Начало перерыва</label>
              <input
                type="time"
                value={form.break_start}
                onChange={(e) => setForm((f) => ({ ...f, break_start: e.target.value }))}
                className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <div className="space-y-1">
              <label className="block text-sm font-medium text-slate-700">Конец перерыва</label>
              <input
                type="time"
                value={form.break_end}
                onChange={(e) => setForm((f) => ({ ...f, break_end: e.target.value }))}
                className="block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-slate-700">Рабочие дни</label>
            <div className="flex gap-2">
              {DAY_LABELS.map((label, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => toggleDay(i)}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    form.working_days.includes(i)
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <Button variant="secondary" onClick={() => setModalOpen(false)}>
              Отмена
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={!form.name || !form.work_start || !form.work_end}
              loading={isSubmitting}
            >
              {editingId ? 'Сохранить' : 'Создать'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
