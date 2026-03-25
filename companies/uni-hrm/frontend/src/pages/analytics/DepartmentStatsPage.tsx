import { useDepartmentStats } from '@/features/documents/hooks';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function DepartmentStatsPage() {
  const { data: stats, isLoading } = useDepartmentStats();

  return (
    <div className="p-6 space-y-6">
      <h1
        className="text-2xl font-bold text-slate-900"
        style={{ fontFamily: 'var(--font-heading)' }}
      >
        Статистика по отделам
      </h1>
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
        {isLoading ? (
          <div>Загрузка...</div>
        ) : (
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={stats ?? []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={120} />
              <Tooltip />
              <Bar
                dataKey="employee_count"
                fill="#4F46E5"
                name="Сотрудников"
                radius={[0, 4, 4, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
