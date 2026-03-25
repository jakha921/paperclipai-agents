import {
  useDashboardStats,
  useTurnoverStats,
  useDepartmentStats,
} from '@/features/documents/hooks';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function HRDashboardPage() {
  const { data: stats, isLoading: statsLoading } = useDashboardStats();
  const { data: turnover } = useTurnoverStats(12);
  const { data: deptStats } = useDepartmentStats();

  if (statsLoading) return <div className="p-6">Загрузка...</div>;

  const kpiCards = [
    {
      label: 'Всего сотрудников',
      value: stats?.total_employees ?? 0,
      color: 'bg-indigo-50 text-indigo-700',
    },
    {
      label: 'Отделов',
      value: stats?.total_departments ?? 0,
      color: 'bg-blue-50 text-blue-700',
    },
    {
      label: 'Открытых вакансий',
      value: stats?.open_vacancies ?? 0,
      color: 'bg-amber-50 text-amber-700',
    },
    {
      label: 'Заявок на отпуск',
      value: stats?.pending_leaves ?? 0,
      color: 'bg-orange-50 text-orange-700',
    },
    {
      label: 'Средняя зарплата',
      value: `${(stats?.avg_salary ?? 0).toLocaleString()} сум`,
      color: 'bg-green-50 text-green-700',
    },
    {
      label: 'Новых в этом месяце',
      value: stats?.new_hires_this_month ?? 0,
      color: 'bg-purple-50 text-purple-700',
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <h1
        className="text-2xl font-bold text-slate-900"
        style={{ fontFamily: 'var(--font-heading)' }}
      >
        HR Dashboard
      </h1>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {kpiCards.map((card) => (
          <div
            key={card.label}
            className={`rounded-xl border p-4 ${card.color} border-transparent shadow-sm`}
          >
            <p className="text-xs font-medium opacity-70">{card.label}</p>
            <p className="text-2xl font-bold mt-1">{card.value}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Turnover LineChart */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <h2 className="text-base font-semibold text-slate-900 mb-4">Текучесть кадров</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={turnover ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="hired_count"
                stroke="#4F46E5"
                name="Принято"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="dismissed_count"
                stroke="#EF4444"
                name="Уволено"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Department BarChart */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <h2 className="text-base font-semibold text-slate-900 mb-4">Сотрудники по отделам</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={deptStats ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar
                dataKey="employee_count"
                fill="#4F46E5"
                name="Сотрудников"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
