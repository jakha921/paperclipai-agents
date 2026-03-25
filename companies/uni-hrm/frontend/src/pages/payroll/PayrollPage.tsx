import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  usePayrolls,
  useBulkCalculatePayroll,
  useApprovePayroll,
  useMarkPaidPayroll,
} from '@/features/payroll';
import type { PayrollStatus, Payroll } from '@/features/payroll';

const STATUS_COLORS: Record<PayrollStatus, string> = {
  DRAFT: 'bg-gray-100 text-gray-700',
  CALCULATED: 'bg-yellow-100 text-yellow-700',
  APPROVED: 'bg-green-100 text-green-700',
  PAID: 'bg-blue-100 text-blue-700',
};

const STATUS_LABELS: Record<PayrollStatus, string> = {
  DRAFT: 'Черновик',
  CALCULATED: 'Рассчитано',
  APPROVED: 'Одобрено',
  PAID: 'Выплачено',
};

export default function PayrollPage() {
  const navigate = useNavigate();
  const currentDate = new Date();
  const [month, setMonth] = useState(currentDate.getMonth() + 1);
  const [year, setYear] = useState(currentDate.getFullYear());

  const { data, isLoading } = usePayrolls({ month, year });
  const bulkCalculate = useBulkCalculatePayroll();
  const approve = useApprovePayroll();
  const markPaid = useMarkPaidPayroll();

  const handleBulkCalculate = () => {
    bulkCalculate.mutate({ month, year });
  };

  const formatMoney = (value: string) =>
    new Intl.NumberFormat('uz-UZ', { style: 'decimal', minimumFractionDigits: 0 }).format(
      parseFloat(value),
    ) + ' сум';

  const items: Payroll[] = data?.results ?? [];

  return (
    <div className="p-6">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold font-heading text-slate-900">Расчёт зарплаты</h1>
          <p className="text-sm text-slate-500 mt-1">Ежемесячный расчёт зарплаты сотрудников</p>
        </div>
        <button
          onClick={handleBulkCalculate}
          disabled={bulkCalculate.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
        >
          {bulkCalculate.isPending ? 'Рассчитывается...' : 'Рассчитать за месяц'}
        </button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <select
          value={month}
          onChange={(e) => setMonth(Number(e.target.value))}
          className="border border-slate-200 rounded-md px-3 py-2 text-sm text-slate-700 bg-white"
        >
          {Array.from({ length: 12 }, (_, i) => (
            <option key={i + 1} value={i + 1}>
              {new Date(2024, i, 1).toLocaleString('ru', { month: 'long' })}
            </option>
          ))}
        </select>
        <select
          value={year}
          onChange={(e) => setYear(Number(e.target.value))}
          className="border border-slate-200 rounded-md px-3 py-2 text-sm text-slate-700 bg-white"
        >
          {[2024, 2025, 2026].map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400">Загрузка...</div>
        ) : items.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            Нет данных. Нажмите "Рассчитать за месяц"
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-slate-600">Сотрудник</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">Оклад</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">Начислено</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">Удержано</th>
                <th className="text-right px-4 py-3 font-medium text-slate-600">К выплате</th>
                <th className="text-center px-4 py-3 font-medium text-slate-600">Статус</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {items.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-slate-900">{p.employee_name}</td>
                  <td className="px-4 py-3 text-right text-slate-600">
                    {formatMoney(p.base_salary)}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-600">
                    {formatMoney(p.gross_salary)}
                  </td>
                  <td className="px-4 py-3 text-right text-red-600">
                    {formatMoney(p.total_deductions)}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-slate-900">
                    {formatMoney(p.net_salary)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span
                      className={`inline-flex px-2 py-1 rounded-sm text-xs font-medium ${STATUS_COLORS[p.status]}`}
                    >
                      {STATUS_LABELS[p.status]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => navigate(`/payroll/${p.id}`)}
                        className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
                      >
                        Детали
                      </button>
                      {p.status === 'CALCULATED' && (
                        <button
                          onClick={() => approve.mutate(p.id)}
                          disabled={approve.isPending}
                          className="text-xs text-green-600 hover:text-green-700 font-medium"
                        >
                          Одобрить
                        </button>
                      )}
                      {p.status === 'APPROVED' && (
                        <button
                          onClick={() => markPaid.mutate({ id: p.id })}
                          disabled={markPaid.isPending}
                          className="text-xs text-blue-600 hover:text-blue-700 font-medium"
                        >
                          Выплачено
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
    </div>
  );
}
