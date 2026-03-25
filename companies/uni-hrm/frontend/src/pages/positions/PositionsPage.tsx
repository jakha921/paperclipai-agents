import { useState } from 'react';
import { Briefcase, Plus } from 'lucide-react';
import {
  usePositions,
  useCreatePosition,
  useDeletePosition,
} from '../../features/departments/api';
import type { CreatePositionData } from '../../features/departments/types';
import {
  Button,
  Card,
  CardHeader,
  CardContent,
  Modal,
  Input,
  PageHeader,
  EmptyState,
  Skeleton,
} from '../../shared/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const positionSchema = z.object({
  code: z.string().min(1),
  name_ru: z.string().min(1),
  name_uz: z.string(),
  name_en: z.string(),
  category: z.enum(['PPS', 'NS', 'AUP', 'UVP', 'POP']),
  is_academic: z.boolean(),
  requirements: z.string(),
  min_salary: z.string().optional(),
  max_salary: z.string().optional(),
});

type PositionFormData = z.infer<typeof positionSchema>;

const CATEGORY_LABELS: Record<string, string> = {
  PPS: 'ППС',
  NS: 'НС',
  AUP: 'АУП',
  UVP: 'УВП',
  POP: 'ПОП',
};

const CATEGORY_COLORS: Record<string, string> = {
  PPS: 'bg-blue-100 text-blue-700',
  NS: 'bg-purple-100 text-purple-700',
  AUP: 'bg-amber-100 text-amber-700',
  UVP: 'bg-green-100 text-green-700',
  POP: 'bg-slate-100 text-slate-700',
};

export default function PositionsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { data, isLoading } = usePositions();
  const createPos = useCreatePosition();
  const deletePos = useDeletePosition();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<PositionFormData>({
    resolver: zodResolver(positionSchema),
    defaultValues: { category: 'AUP', is_academic: false, name_uz: '', name_en: '', requirements: '' },
  });

  const onSubmit = async (formData: PositionFormData) => {
    const payload: CreatePositionData = {
      code: formData.code,
      name: { ru: formData.name_ru, uz: formData.name_uz, en: formData.name_en },
      category: formData.category,
      is_academic: formData.is_academic,
      min_salary: formData.min_salary || null,
      max_salary: formData.max_salary || null,
      requirements: formData.requirements,
    };
    await createPos.mutateAsync(payload);
    setIsModalOpen(false);
    reset();
  };

  const positions = data?.results ?? [];

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Должности"
        description="Справочник должностей"
        actions={
          <Button onClick={() => setIsModalOpen(true)}>
            <Plus className="h-4 w-4 mr-2" /> Добавить
          </Button>
        }
      />

      <Card>
        <CardHeader>
          <h3 className="text-base font-semibold text-slate-900">
            Список должностей ({data?.count ?? 0})
          </h3>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          ) : positions.length === 0 ? (
            <EmptyState
              icon={<Briefcase className="h-12 w-12 text-slate-300" />}
              title="Нет должностей"
              description="Добавьте первую должность"
              action={<Button onClick={() => setIsModalOpen(true)}>Добавить</Button>}
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Код
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Название
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Категория
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Зарплата
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Академическая
                    </th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {positions.map((pos) => (
                    <tr key={pos.id} className="border-b border-slate-50 hover:bg-slate-50">
                      <td className="py-3 px-4 text-sm font-mono text-slate-600">{pos.code}</td>
                      <td className="py-3 px-4 text-sm font-medium text-slate-800">
                        {pos.name?.ru || pos.code}
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`text-xs px-2 py-1 rounded-full font-medium ${CATEGORY_COLORS[pos.category]}`}
                        >
                          {CATEGORY_LABELS[pos.category]}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-600">
                        {pos.min_salary && pos.max_salary
                          ? `${Number(pos.min_salary).toLocaleString()} — ${Number(pos.max_salary).toLocaleString()}`
                          : '—'}
                      </td>
                      <td className="py-3 px-4">
                        {pos.is_academic ? (
                          <span className="text-xs px-2 py-1 rounded-full bg-indigo-100 text-indigo-700">
                            Да
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400">—</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => deletePos.mutate(pos.id)}
                          className="text-red-400 hover:text-red-600 text-xs"
                        >
                          Удалить
                        </button>
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
        open={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          reset();
        }}
        title="Новая должность"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700">Код *</label>
              <Input {...register('code')} placeholder="PROF" className="mt-1" />
              {errors.code && <p className="text-xs text-red-500 mt-1">{errors.code.message}</p>}
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Категория *</label>
              <select
                {...register('category')}
                className="mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              >
                {Object.entries(CATEGORY_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Название (RU) *</label>
            <Input {...register('name_ru')} placeholder="Профессор" className="mt-1" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-slate-700">Мин. зарплата</label>
              <Input
                {...register('min_salary')}
                placeholder="5000000"
                type="number"
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-slate-700">Макс. зарплата</label>
              <Input
                {...register('max_salary')}
                placeholder="10000000"
                type="number"
                className="mt-1"
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              {...register('is_academic')}
              id="is_academic"
              className="rounded"
            />
            <label htmlFor="is_academic" className="text-sm text-slate-700">
              Академическая должность
            </label>
          </div>
          <div className="flex gap-3 pt-2">
            <Button type="submit" disabled={createPos.isPending} className="flex-1">
              {createPos.isPending ? 'Создание...' : 'Создать'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setIsModalOpen(false);
                reset();
              }}
            >
              Отмена
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
