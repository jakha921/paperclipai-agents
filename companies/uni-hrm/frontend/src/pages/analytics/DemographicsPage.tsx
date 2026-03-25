import { useDemographics } from '@/features/documents/hooks';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#4F46E5', '#818CF8', '#C7D2FE', '#6366F1', '#3730A3'];

export default function DemographicsPage() {
  const { data: demo, isLoading } = useDemographics();

  const genderData = Object.entries(demo?.gender_distribution ?? {}).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="p-6 space-y-6">
      <h1
        className="text-2xl font-bold text-slate-900"
        style={{ fontFamily: 'var(--font-heading)' }}
      >
        Демография
      </h1>
      {isLoading ? (
        <div>Загрузка...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h2 className="text-base font-semibold text-slate-900 mb-4">
              Распределение по полу
            </h2>
            {genderData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={genderData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label
                  >
                    {genderData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-500 text-sm">Нет данных</p>
            )}
          </div>
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
            <h2 className="text-base font-semibold text-slate-900 mb-2">Статистика</h2>
            <p className="text-3xl font-bold text-indigo-600">{demo?.total ?? 0}</p>
            <p className="text-sm text-slate-500">Всего сотрудников</p>
          </div>
        </div>
      )}
    </div>
  );
}
