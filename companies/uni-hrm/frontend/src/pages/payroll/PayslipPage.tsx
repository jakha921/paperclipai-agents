import { useParams } from 'react-router-dom';
import { usePayslip } from '@/features/payroll';

const MONTH_NAMES = [
  '',
  'Январь',
  'Февраль',
  'Март',
  'Апрель',
  'Май',
  'Июнь',
  'Июль',
  'Август',
  'Сентябрь',
  'Октябрь',
  'Ноябрь',
  'Декабрь',
];

export default function PayslipPage() {
  const { id } = useParams<{ id: string }>();
  const { data: payroll, isLoading } = usePayslip(Number(id));

  const formatMoney = (value: string) =>
    new Intl.NumberFormat('uz-UZ', { style: 'decimal', minimumFractionDigits: 2 }).format(
      parseFloat(value),
    ) + ' сум';

  if (isLoading) return <div className="p-12 text-center text-slate-400">Загрузка...</div>;
  if (!payroll) return <div className="p-12 text-center text-slate-400">Не найдено</div>;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold font-heading text-slate-900">Расчётный лист</h1>
          <p className="text-slate-500 text-sm mt-1">
            {payroll.employee_name} — {MONTH_NAMES[payroll.month]} {payroll.year}
          </p>
        </div>
        <button
          onClick={() => window.print()}
          className="px-4 py-2 border border-slate-200 rounded-md text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
        >
          Распечатать
        </button>
      </div>

      {/* Attendance summary */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Рабочих дней', value: payroll.working_days_in_month },
          { label: 'Отработано', value: payroll.days_worked },
          { label: 'В отпуске', value: payroll.days_on_leave },
          { label: 'Прогулы', value: payroll.days_absent },
        ].map((item) => (
          <div key={item.label} className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="text-2xl font-bold text-slate-900">{item.value}</div>
            <div className="text-xs text-slate-500 mt-1">{item.label}</div>
          </div>
        ))}
      </div>

      {/* Two-column breakdown */}
      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Начисления */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="text-base font-semibold text-slate-900 mb-4">Начисления</h3>
          <div className="space-y-3">
            {[
              { label: 'Оклад', value: payroll.base_salary },
              { label: 'Надбавка за степень', value: payroll.academic_bonus },
              { label: 'Надбавка за должность', value: payroll.position_bonus },
              { label: 'Надбавка за стаж', value: payroll.seniority_bonus },
              { label: 'Прочие надбавки', value: payroll.other_allowances },
              { label: 'Сверхурочные', value: payroll.overtime_payment },
            ].map((row) => (
              <div key={row.label} className="flex justify-between text-sm">
                <span className="text-slate-600">{row.label}</span>
                <span className="text-slate-900 font-medium">{formatMoney(row.value)}</span>
              </div>
            ))}
            <div className="border-t border-slate-200 pt-3 flex justify-between text-sm font-semibold">
              <span className="text-slate-900">Итого начислено</span>
              <span className="text-slate-900">{formatMoney(payroll.gross_salary)}</span>
            </div>
          </div>
        </div>

        {/* Удержания */}
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="text-base font-semibold text-slate-900 mb-4">Удержания</h3>
          <div className="space-y-3">
            {[
              { label: 'НДФЛ (12%)', value: payroll.ndfl },
              { label: 'ИНПС работника (0.1%)', value: payroll.inps_employee },
              { label: 'Прочие удержания', value: payroll.other_deductions },
            ].map((row) => (
              <div key={row.label} className="flex justify-between text-sm">
                <span className="text-slate-600">{row.label}</span>
                <span className="text-red-600 font-medium">{formatMoney(row.value)}</span>
              </div>
            ))}
            <div className="border-t border-slate-200 pt-3 flex justify-between text-sm font-semibold">
              <span className="text-slate-900">Итого удержано</span>
              <span className="text-red-600">{formatMoney(payroll.total_deductions)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Net salary */}
      <div className="bg-indigo-50 rounded-xl border border-indigo-200 p-6 flex items-center justify-between">
        <div>
          <div className="text-sm font-medium text-indigo-700">К выплате</div>
          <div className="text-4xl font-bold text-indigo-900 mt-1">
            {formatMoney(payroll.net_salary)}
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-indigo-600">Коэффициент посещаемости</div>
          <div className="text-2xl font-bold text-indigo-700">
            {(parseFloat(payroll.attendance_ratio) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Employer taxes */}
      <div className="mt-6 bg-white rounded-xl border border-slate-200 p-6">
        <h3 className="text-base font-semibold text-slate-900 mb-4">Обязательства работодателя</h3>
        <div className="grid grid-cols-2 gap-4">
          {[
            { label: 'Социальный налог (12%)', value: payroll.employer_social_tax },
            { label: 'ИНПС работодателя (0.1%)', value: payroll.employer_inps },
          ].map((row) => (
            <div key={row.label} className="flex justify-between text-sm">
              <span className="text-slate-600">{row.label}</span>
              <span className="text-slate-900 font-medium">{formatMoney(row.value)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
