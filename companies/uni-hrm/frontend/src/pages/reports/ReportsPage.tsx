import { useState } from 'react';
import {
  useDownloadPayrollExcel,
  useDownloadEmployeesExcel,
} from '@/features/documents/hooks';

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ReportsPage() {
  const [payrollPeriod, setPayrollPeriod] = useState('');
  const payrollMutation = useDownloadPayrollExcel();
  const employeesMutation = useDownloadEmployeesExcel();

  const handlePayrollExcel = async () => {
    const blob = await payrollMutation.mutateAsync({
      period_id: payrollPeriod || undefined,
    });
    downloadBlob(blob, 'payroll.xlsx');
  };

  const handleEmployeesExcel = async () => {
    const blob = await employeesMutation.mutateAsync({});
    downloadBlob(blob, 'employees.xlsx');
  };

  return (
    <div className="p-6 space-y-6">
      <h1
        className="text-2xl font-bold text-slate-900"
        style={{ fontFamily: 'var(--font-heading)' }}
      >
        Отчёты
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
          <h2 className="text-base font-semibold text-slate-900">Ведомость зарплат (Excel)</h2>
          <p className="text-sm text-slate-500">Выгрузка расчётного листа за период</p>
          <input
            type="text"
            placeholder="ID периода (опционально)"
            value={payrollPeriod}
            onChange={(e) => setPayrollPeriod(e.target.value)}
            className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={handlePayrollExcel}
            disabled={payrollMutation.isPending}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {payrollMutation.isPending ? 'Генерация...' : 'Скачать Excel'}
          </button>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4">
          <h2 className="text-base font-semibold text-slate-900">Список сотрудников (Excel)</h2>
          <p className="text-sm text-slate-500">Полный список сотрудников с данными</p>
          <button
            onClick={handleEmployeesExcel}
            disabled={employeesMutation.isPending}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            {employeesMutation.isPending ? 'Генерация...' : 'Скачать Excel'}
          </button>
        </div>
      </div>
    </div>
  );
}
