import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Plus } from 'lucide-react';
import {
  useVacancies,
  useCreateVacancy,
  usePublishVacancy,
  useCloseVacancy,
} from '@/features/recruitment';
import type { CreateVacancyData, VacancyStatus } from '@/features/recruitment';
import { useDepartments } from '@/features/departments';
import {
  VACANCY_STATUS_COLORS,
  VACANCY_STATUS_LABELS,
} from '@/shared/constants/statuses';

function getVacancyTitle(title: CreateVacancyData['title'] | string): string {
  if (typeof title === 'object') {
    return title.ru ?? title.en ?? '';
  }
  return String(title);
}

export default function VacanciesPage() {
  const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);

  const { data, isLoading } = useVacancies();
  const createVacancy = useCreateVacancy();
  const publishVacancy = usePublishVacancy();
  const closeVacancy = useCloseVacancy();
  const { data: depsData } = useDepartments();

  const vacancies = data?.results ?? [];
  const departments = depsData?.results ?? [];

  const handleCreate = async (payload: CreateVacancyData) => {
    await createVacancy.mutateAsync(payload);
    setShowModal(false);
  };

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-14 bg-slate-200 animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold font-heading text-slate-900">Вакансии</h1>
          <p className="text-sm text-slate-500 mt-1">{data?.count ?? 0} вакансий</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Добавить вакансию
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {vacancies.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400">
            <Briefcase className="h-12 w-12 mb-3" />
            <p className="text-sm font-medium">Нет вакансий</p>
            <p className="text-xs mt-1">Создайте первую вакансию</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50">
                <th className="text-left px-4 py-3 font-medium text-slate-600">Название</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Отдел</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Статус</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Кандидатов</th>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Дедлайн</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">Действия</th>
              </tr>
            </thead>
            <tbody>
              {vacancies.map((v) => (
                <tr
                  key={v.id}
                  className="border-b border-slate-100 hover:bg-slate-50 cursor-pointer transition-colors"
                  onClick={() => navigate(`/recruitment/vacancies/${v.id}`)}
                >
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {getVacancyTitle(v.title)}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{v.department_name}</td>
                  <td className="px-4 py-3">
                    <StatusBadge status={v.status} />
                  </td>
                  <td className="px-4 py-3 text-slate-600">{v.candidates_count}</td>
                  <td className="px-4 py-3 text-slate-600">{v.deadline ?? '—'}</td>
                  <td
                    className="px-4 py-3 text-right"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <div className="flex items-center justify-end gap-2">
                      {v.status === 'DRAFT' && (
                        <button
                          onClick={() => publishVacancy.mutate(v.id)}
                          disabled={publishVacancy.isPending}
                          className="px-3 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 rounded hover:bg-emerald-200 transition-colors disabled:opacity-50"
                        >
                          Опубликовать
                        </button>
                      )}
                      {v.status === 'OPEN' && (
                        <button
                          onClick={() => closeVacancy.mutate(v.id)}
                          disabled={closeVacancy.isPending}
                          className="px-3 py-1 text-xs font-medium bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors disabled:opacity-50"
                        >
                          Закрыть
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <CreateVacancyModal
          onClose={() => setShowModal(false)}
          onSubmit={handleCreate}
          isLoading={createVacancy.isPending}
          departments={departments}
        />
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: VacancyStatus }) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${VACANCY_STATUS_COLORS[status] ?? ''}`}
    >
      {VACANCY_STATUS_LABELS[status] ?? status}
    </span>
  );
}

function CreateVacancyModal({
  onClose,
  onSubmit,
  isLoading,
  departments,
}: {
  onClose: () => void;
  onSubmit: (data: CreateVacancyData) => void;
  isLoading: boolean;
  departments: Array<{ id: string; name: Record<string, string> | string }>;
}) {
  const [titleRu, setTitleRu] = useState('');
  const [deptId, setDeptId] = useState('');
  const [count, setCount] = useState('1');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!titleRu || !deptId) return;
    onSubmit({ title: { ru: titleRu }, department: deptId, vacancies_count: Number(count) });
  };

  const getDeptName = (name: Record<string, string> | string) => {
    if (typeof name === 'object') return name.ru ?? name.en ?? '';
    return name;
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-md w-full max-w-md p-6 space-y-4">
        <h2 className="text-lg font-semibold font-heading text-slate-900">Новая вакансия</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Название (RU)
            </label>
            <input
              value={titleRu}
              onChange={(e) => setTitleRu(e.target.value)}
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Название вакансии"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Отдел</label>
            <select
              value={deptId}
              onChange={(e) => setDeptId(e.target.value)}
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            >
              <option value="">Выберите отдел</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>
                  {getDeptName(d.name)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Количество мест
            </label>
            <input
              type="number"
              value={count}
              onChange={(e) => setCount(e.target.value)}
              min="1"
              className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200 transition-colors"
            >
              Отмена
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Создание...' : 'Создать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
