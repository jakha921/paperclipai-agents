import { useState } from 'react';
import {
  useEmployeeSalaries,
  useCreateEmployeeSalary,
  useUpdateEmployeeSalary,
} from '@/features/payroll';
import type { EmployeeSalary } from '@/features/payroll';
import { useEmployees } from '@/features/employees/api';

interface SalaryFormState {
  employee: string;
  base_salary: string;
  academic_bonus_pct: string;
  position_bonus_pct: string;
  seniority_bonus_pct: string;
  other_allowances: string;
  effective_from: string;
}

const INITIAL_FORM: SalaryFormState = {
  employee: '',
  base_salary: '',
  academic_bonus_pct: '0',
  position_bonus_pct: '0',
  seniority_bonus_pct: '0',
  other_allowances: '0',
  effective_from: '',
};

export default function SalaryConfigPage() {
  const { data, isLoading } = useEmployeeSalaries({ is_active: true });
  const createSalary = useCreateEmployeeSalary();
  const updateSalary = useUpdateEmployeeSalary();
  const { data: employeesData } = useEmployees({ status: 'ACTIVE' });
  const [editingSalary, setEditingSalary] = useState<EmployeeSalary | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<SalaryFormState>(INITIAL_FORM);

  const formatMoney = (value: string) =>
    new Intl.NumberFormat('uz-UZ', { style: 'decimal', minimumFractionDigits: 0 }).format(
      parseFloat(value),
    ) + ' сум';

  const handleEdit = (salary: EmployeeSalary) => {
    setEditingSalary(salary);
    setForm({
      employee: String(salary.employee),
      base_salary: salary.base_salary,
      academic_bonus_pct: salary.academic_bonus_pct,
      position_bonus_pct: salary.position_bonus_pct,
      seniority_bonus_pct: salary.seniority_bonus_pct,
      other_allowances: salary.other_allowances,
      effective_from: salary.effective_from,
    });
    setShowModal(true);
  };

  const handleAdd = () => {
    setEditingSalary(null);
    setForm(INITIAL_FORM);
    setShowModal(true);
  };

  const handleSubmit = () => {
    const payload = {
      employee: Number(form.employee),
      base_salary: form.base_salary,
      academic_bonus_pct: form.academic_bonus_pct,
      position_bonus_pct: form.position_bonus_pct,
      seniority_bonus_pct: form.seniority_bonus_pct,
      other_allowances: form.other_allowances,
      effective_from: form.effective_from,
    };

    if (editingSalary) {
      updateSalary.mutate(
        { id: editingSalary.id, data: payload },
        { onSuccess: () => setShowModal(false) },
      );
    } else {
      createSalary.mutate(payload, {
        onSuccess: () => setShowModal(false),
      });
    }
  };

  const items: EmployeeSalary[] = data?.results ?? [];

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold font-heading text-slate-900">Настройка зарплат</h1>
          <p className="text-sm text-slate-500 mt-1">Оклады и надбавки сотрудников</p>
        </div>
        <button
          onClick={handleAdd}
          className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 transition-colors"
        >
          + Добавить
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400">Загрузка...</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Сотрудник</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">Оклад</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">Итого (gross)</th>
                <th className="text-center px-4 py-3 font-medium text-slate-600">Действует с</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((s) => (
                <tr key={s.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {employeesData?.results?.find((e) => String(e.id) === String(s.employee))
                      ?.full_name ?? `#${s.employee}`}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-600">
                    {formatMoney(s.base_salary)}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-slate-900">
                    {formatMoney(s.gross_monthly)}
                  </td>
                  <td className="px-4 py-3 text-center text-slate-500">{s.effective_from}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleEdit(s)}
                      className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                    >
                      Изменить
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-md p-6 w-full max-w-md">
            <h2 className="text-lg font-semibold text-slate-900 mb-4">
              {editingSalary ? 'Изменить зарплату' : 'Добавить зарплату'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Сотрудник
                </label>
                <select
                  value={form.employee}
                  onChange={(e) => setForm({ ...form, employee: e.target.value })}
                  className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm"
                  disabled={!!editingSalary}
                >
                  <option value="">Выберите сотрудника</option>
                  {employeesData?.results?.map((e) => (
                    <option key={e.id} value={e.id}>
                      {e.full_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Оклад (сум)
                </label>
                <input
                  type="number"
                  value={form.base_salary}
                  onChange={(e) => setForm({ ...form, base_salary: e.target.value })}
                  className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm"
                />
              </div>
              {[
                { key: 'academic_bonus_pct' as const, label: 'Надбавка за степень (%)' },
                { key: 'position_bonus_pct' as const, label: 'Надбавка за должность (%)' },
                { key: 'seniority_bonus_pct' as const, label: 'Надбавка за стаж (%)' },
              ].map(({ key, label }) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-slate-700 mb-1">{label}</label>
                  <input
                    type="number"
                    step="0.01"
                    value={form[key]}
                    onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                    className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm"
                  />
                </div>
              ))}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Действует с
                </label>
                <input
                  type="date"
                  value={form.effective_from}
                  onChange={(e) => setForm({ ...form, effective_from: e.target.value })}
                  className="w-full border border-slate-200 rounded-md px-3 py-2 text-sm"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 mt-6">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-sm text-slate-600 hover:text-slate-900"
              >
                Отмена
              </button>
              <button
                onClick={handleSubmit}
                disabled={createSalary.isPending || updateSalary.isPending}
                className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
