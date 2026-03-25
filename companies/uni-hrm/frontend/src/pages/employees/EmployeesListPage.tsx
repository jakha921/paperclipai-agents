import { useState } from 'react';
import { Users, Plus, Search } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useEmployees } from '../../features/employees/api';
import { useDepartments } from '../../features/departments/api';
import type { EmployeeFilters } from '../../features/employees/types';
import {
  Button,
  Card,
  CardContent,
  PageHeader,
  EmptyState,
  Skeleton,
} from '../../shared/ui';

const STATUS_LABELS: Record<string, string> = {
  ACTIVE: 'Работает',
  ON_LEAVE: 'В отпуске',
  DISMISSED: 'Уволен',
};
const STATUS_COLORS: Record<string, string> = {
  ACTIVE: 'bg-emerald-100 text-emerald-700',
  ON_LEAVE: 'bg-amber-100 text-amber-700',
  DISMISSED: 'bg-red-100 text-red-700',
};
const CONTRACT_LABELS: Record<string, string> = {
  PERMANENT: 'Основное',
  PART_TIME: 'Совместит.',
  HOURLY: 'Почасовое',
};

export default function EmployeesListPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<EmployeeFilters>({});
  const [searchValue, setSearchValue] = useState('');
  const { data, isLoading } = useEmployees({ ...filters, search: searchValue || undefined });
  const { data: depts } = useDepartments();

  const employees = data?.results ?? [];
  const total = data?.count ?? 0;

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchValue(e.target.value);
  };

  return (
    <div className="p-6 space-y-6">
      <PageHeader
        title="Сотрудники"
        description={`Всего: ${total} сотрудников`}
        actions={
          <Button onClick={() => navigate('/employees/new')}>
            <Plus className="h-4 w-4 mr-2" /> Добавить
          </Button>
        }
      />

      {/* Фильтры */}
      <Card className="p-4">
        <div className="flex flex-wrap gap-3">
          <div className="relative flex-1 min-w-48">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Поиск по ФИО или табельному..."
              value={searchValue}
              onChange={handleSearch}
              className="w-full pl-9 pr-4 py-2 rounded-md border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <select
            value={filters.status ?? ''}
            onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value || undefined }))}
            className="px-3 py-2 rounded-md border border-slate-200 text-sm text-slate-600"
          >
            <option value="">Все статусы</option>
            {Object.entries(STATUS_LABELS).map(([v, l]) => (
              <option key={v} value={v}>
                {l}
              </option>
            ))}
          </select>
          <select
            value={filters.department ?? ''}
            onChange={(e) =>
              setFilters((f) => ({ ...f, department: e.target.value || undefined }))
            }
            className="px-3 py-2 rounded-md border border-slate-200 text-sm text-slate-600"
          >
            <option value="">Все подразделения</option>
            {depts?.results?.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name_display || d.name?.ru}
              </option>
            ))}
          </select>
        </div>
      </Card>

      <Card>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3 p-4">
              {Array.from({ length: 8 }).map((_, i) => (
                <Skeleton key={i} className="h-14 w-full" />
              ))}
            </div>
          ) : employees.length === 0 ? (
            <EmptyState
              icon={<Users className="h-12 w-12 text-slate-300" />}
              title="Нет сотрудников"
              description="Добавьте первого сотрудника"
              action={
                <Button onClick={() => navigate('/employees/new')}>Добавить</Button>
              }
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-100">
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Сотрудник
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Табельный №
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Подразделение
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Должность
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Контракт
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Статус
                    </th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-slate-500 uppercase">
                      Найм
                    </th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {employees.map((emp) => (
                    <tr
                      key={emp.id}
                      className="border-b border-slate-50 hover:bg-slate-50 cursor-pointer"
                      onClick={() => navigate(`/employees/${emp.id}`)}
                    >
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-3">
                          <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 text-sm font-medium flex-shrink-0">
                            {emp.last_name?.[0]}
                            {emp.first_name?.[0]}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-slate-800">{emp.full_name}</p>
                            <p className="text-xs text-slate-400">{emp.phone}</p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4 text-sm font-mono text-slate-500">
                        {emp.employee_number}
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-600">{emp.department_name}</td>
                      <td className="py-3 px-4 text-sm text-slate-600">{emp.position_name}</td>
                      <td className="py-3 px-4">
                        <span className="text-xs text-slate-500">
                          {CONTRACT_LABELS[emp.contract_type]}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`text-xs px-2 py-1 rounded-full font-medium ${STATUS_COLORS[emp.status]}`}
                        >
                          {STATUS_LABELS[emp.status]}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-sm text-slate-500">{emp.hire_date}</td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/employees/${emp.id}`);
                          }}
                          className="text-indigo-600 hover:text-indigo-800 text-xs font-medium"
                        >
                          Открыть
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
    </div>
  );
}
